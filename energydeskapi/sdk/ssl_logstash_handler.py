import logging
import socket
import ssl
import json
# Problems with the original logger and SSL

class SSLTCPLogstashHandler(logging.Handler):
    """
    Python logging handler for Logstash with SSL/TLS support.
    Sends log messages over TCP with SSL encryption.
    Compatible with LogstashFormatterVersion1 from python-logstash.
    """

    def __init__(self, host, port, message_type='python-logstash', tags=None, 
                 version=1, ssl_enable=True, ssl_verify=True, timeout=5, fqdn=False,
                 customer=None, environment=None, appname=None):
        """
        Initialize the SSL TCP Logstash handler.
        
        Args:
            host: Logstash server hostname
            port: Logstash server port
            message_type: Type field for logstash messages
            tags: List of tags to add to log messages (e.g., [customer, environment, appname])
            version: Logstash event schema version (0 or 1)
            ssl_enable: Whether to use SSL/TLS encryption
            ssl_verify: Whether to verify SSL certificates
            timeout: Socket timeout in seconds
            fqdn: Use fully qualified domain name for host field
            customer: Customer identifier (added as explicit field in logs)
            environment: Environment identifier (added as explicit field in logs)
            appname: Application name (added as explicit field in logs)
        """
        super().__init__()
        self.host = host
        self.port = port
        self.message_type = message_type
        self.tags = tags or []
        self.version = version
        self.ssl_enable = ssl_enable
        self.ssl_verify = ssl_verify
        self.timeout = timeout
        self.fqdn = fqdn
        self.sock = None
        self._fallback_formatter = None
        
        # Store customer, environment, appname as explicit fields
        self.customer = customer
        self.environment = environment
        self.appname = appname
        
        # Try to use the standard LogstashFormatterVersion1 if available
        try:
            from logstash.formatter import LogstashFormatterVersion1
            self._fallback_formatter = LogstashFormatterVersion1(
                message_type=message_type,
                tags=tags,
                fqdn=fqdn
            )
        except ImportError:
            # If python-logstash not available, we'll use our own formatter
            pass
        
    def makeSocket(self):
        """Create and return a socket connection to logstash."""
        try:
            # Create a TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            if self.ssl_enable:
                # Wrap socket with SSL
                context = ssl.create_default_context()
                if not self.ssl_verify:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                
                sock = context.wrap_socket(sock, server_hostname=self.host)
            
            sock.connect((self.host, self.port))
            return sock
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")
    
    def makeLogstashMessage(self, record):
        """
        Create a logstash-formatted message from a log record.
        Uses the same format as LogstashFormatterVersion1 for consistency.
        
        Args:
            record: Python LogRecord
            
        Returns:
            dict: Logstash-formatted message compatible with ELK
        """
        # If we have the standard formatter, use it for consistency
        if self._fallback_formatter:
            try:
                # The formatter returns a formatted string, but we need the dict
                # So we'll call its internal message construction
                return self._fallback_formatter._create_message_dict(record)
            except:
                pass  # Fall back to our own implementation
        
        # Build message compatible with LogstashFormatterVersion1 format
        message = {
            '@timestamp': self.formatTime(record),
            '@version': str(self.version),
            'message': record.getMessage(),
            'host': socket.getfqdn() if self.fqdn else socket.gethostname(),
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,
            'level': record.levelname,
            'logger_name': record.name,
        }
        
        # Add customer, environment, appname as explicit fields for easy filtering
        if self.customer:
            message['customer'] = self.customer
        if self.environment:
            message['environment'] = self.environment
        if self.appname:
            message['appname'] = self.appname
        
        # Add standard fields that match python-logstash format
        if hasattr(record, 'funcName') and record.funcName:
            message['funcName'] = record.funcName
        if hasattr(record, 'lineno'):
            message['lineno'] = record.lineno
        if hasattr(record, 'process'):
            message['process'] = record.process
        if hasattr(record, 'processName'):
            message['processName'] = record.processName
        if hasattr(record, 'thread'):
            message['thread'] = record.thread
        if hasattr(record, 'threadName'):
            message['threadName'] = record.threadName
            
        # Add exception info if present
        if record.exc_info:
            import traceback
            message['exc_info'] = ''.join(traceback.format_exception(*record.exc_info))
        
        # Add stack_info if present (Python 3.2+)
        if hasattr(record, 'stack_info') and record.stack_info:
            message['stack_info'] = record.stack_info
            
        # Add custom fields from record (extra={} in log calls)
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info', 'taskName']:
                try:
                    # Only add JSON-serializable values
                    json.dumps(value)
                    message[key] = value
                except (TypeError, ValueError):
                    message[key] = str(value)
                
        return message
    
    def formatTime(self, record):
        """Format timestamp in ISO 8601 format for logstash."""
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def emit(self, record):
        """
        Emit a log record.
        
        Args:
            record: Python LogRecord
        """
        try:
            # Create logstash message
            message = self.makeLogstashMessage(record)
            
            # Convert to JSON and add newline
            data = json.dumps(message) + '\n'
            
            # Ensure socket is connected
            if self.sock is None:
                self.sock = self.makeSocket()
            
            # Send data
            self.sock.sendall(data.encode('utf-8'))
            
        except (BrokenPipeError, ConnectionError, OSError, socket.error) as e:
            # Connection lost, try to reconnect once
            self.sock = None
            try:
                self.sock = self.makeSocket()
                message = self.makeLogstashMessage(record)
                data = json.dumps(message) + '\n'
                self.sock.sendall(data.encode('utf-8'))
            except Exception:
                # If reconnection fails, let it propagate
                raise
        except Exception as e:
            self.handleError(record)
    
    def close(self):
        """Close the socket connection."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None
        super().close()

