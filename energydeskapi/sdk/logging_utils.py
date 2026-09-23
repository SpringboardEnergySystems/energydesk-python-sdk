from typing import Optional, Any

import atexit
import logging
import os
import queue
import environ
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
from dataclasses import dataclass
from energydeskapi.sdk.common_utils import load_class_from_string
from energydeskapi.sdk.ssl_logstash_handler import SSLTCPLogstashHandler
logger = logging.getLogger(__name__)


class HealthProbeFilter(logging.Filter):
    """Drops Kubernetes liveness/readiness/health-check request log lines."""
    PATHS = ("/health", "/liveness", "/readiness", "kube-probe")

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(p in msg for p in self.PATHS)


class UvicornAccessFieldsFilter(logging.Filter):
    """Unpacks uvicorn.access's positional args into named record attributes
    (client_addr, method, path, http_version, status_code) so they become
    top-level, filterable fields in Logstash/Kibana instead of buried in the
    formatted message string."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name == "uvicorn.access" and isinstance(record.args, tuple) and len(record.args) == 5:
            record.client_addr, record.method, record.path, record.http_version, record.status_code = record.args
        return True


class _DroppingQueueHandler(QueueHandler):
    """QueueHandler that drops records instead of blocking when the queue is
    full, and preserves exc_info/args on the queued record so the downstream
    handler (running on the listener thread) can still format tracebacks and
    read the uvicorn.access fields unpacked by UvicornAccessFieldsFilter."""

    def __init__(self, q):
        super().__init__(q)
        self.dropped = 0

    def enqueue(self, record):
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            self.dropped += 1

    def prepare(self, record):
        # The base QueueHandler.prepare() formats the message and clears
        # exc_info/args, which is meant for crossing a process boundary. This
        # queue stays within one process (feeding a listener thread), so pass
        # the record through unchanged — the listener's handler still needs
        # exc_info for tracebacks and args for UvicornAccessFieldsFilter.
        return record


@dataclass(frozen=True)
class LogstashConfig:
    host: str
    port : int
    customer: str= "cust1"
    environment: str = "dev1"
    appname: str = "SDK"

def get_environment_value(parameter: str, default: Any) -> Any:
    env = environ.Env()
    outvalue = default
    if parameter in os.environ:
        outvalue = env(parameter)
    return outvalue

def get_logfile_format(servicetag):
    format="%(asctime)s srv_" + servicetag + " %(name)-12s %(levelname)-8s %(message)s"
    return format

def get_logstash_format():
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    return format

def get_consolelog_format():
    format="%(asctime)s %(levelname)-8s %(message)s"
    return format

def get_loglevel_from_str(strlevel: str) -> int:
    if strlevel=="DEBUG":
        return logging.DEBUG
    if strlevel=="INFO":
        return logging.INFO
    if strlevel=="WARNING":
        return logging.WARNING
    if strlevel=="ERROR":
        return logging.ERROR
    return logging.INFO

def get_loglevel_to_str(level: int) -> str:
    if level==logging.DEBUG:
        return "DEBUG"
    if level==logging.INFO:
        return "INFO"
    if level==logging.WARNING:
        return "WARNING"
    if level==logging.ERROR:
        return "ERROR"
    return "INFO"

# Tracks the currently-running QueueListener so a repeated setup_service_logging()
# call (logging.basicConfig(force=True) replaces root handlers each time) stops the
# old listener thread instead of leaking it.
_active_queue_listener: Optional[QueueListener] = None


def _stop_active_queue_listener() -> None:
    global _active_queue_listener
    if _active_queue_listener is not None:
        try:
            _active_queue_listener.stop()
        except Exception:
            pass
        _active_queue_listener = None


def create_tcp_handler_queued(handler: logging.Handler) -> logging.Handler:
    """Wraps a (typically slow/blocking) handler with a QueueHandler backed by a
    QueueListener running on its own thread, so callers only ever enqueue —
    all socket I/O happens off the caller's thread. Records are dropped (and
    counted) rather than blocking the caller when the queue fills up."""
    global _active_queue_listener
    _stop_active_queue_listener()
    maxsize = int(os.environ.get("LOGSTASH_QUEUE_MAXSIZE", "10000"))
    q = queue.Queue(maxsize=maxsize)
    listener = QueueListener(q, handler, respect_handler_level=True)
    listener.start()
    atexit.register(listener.stop)
    _active_queue_listener = listener

    queue_handler = _DroppingQueueHandler(q)
    queue_handler.setLevel(handler.level)
    return queue_handler


def setup_service_logging(servicetag: str, file_level: int=logging.INFO, console_level: int=logging.INFO, enable_logstash_conf:LogstashConfig=None):
    console_level=get_loglevel_from_str(get_environment_value("OVERRIDE_CONSOLE_LOGLEVEL", get_loglevel_to_str(console_level)))
    file_level=get_loglevel_from_str(get_environment_value("OVERRIDE_FILE_LOGLEVEL", get_loglevel_to_str(file_level)))

    def create_console_handler() -> logging.StreamHandler:
        console = logging.StreamHandler()
        formatter_console = logging.Formatter(get_consolelog_format())
        console.setFormatter(formatter_console)
        console.setLevel(console_level)
        return console

    def create_tcp_handler(host, port):
        try:
            # Get timeout from environment or use default of 3 seconds
            timeout = int(os.environ.get('LOGSTASH_TIMEOUT', '3'))
            loglev = os.environ.get('LOGSTASH_LOGLEVEL', 'INFO')
            
            # Check if SSL is enabled (default to True for security)
            ssl_enabled = os.environ.get('LOGSTASH_SSL_ENABLE', 'true').upper() == 'TRUE'
            ssl_verify = os.environ.get('LOGSTASH_SSL_VERIFY', 'false').upper() == 'TRUE'

            if ssl_enabled:
                # Use SSL-enabled handler with explicit fields
                print(f"  Creating SSL/TLS logstash handler (verify={ssl_verify}, timeout={timeout}s)")
                handler = SSLTCPLogstashHandler(
                    host=host,
                    port=port,
                    version=1,
                    message_type='python-logstash',
                    tags=[enable_logstash_conf.customer, enable_logstash_conf.environment, enable_logstash_conf.appname],
                    ssl_enable=True,
                    ssl_verify=ssl_verify,
                    timeout=timeout,
                    fqdn=False,
                    customer=enable_logstash_conf.customer,
                    environment=enable_logstash_conf.environment,
                    appname=enable_logstash_conf.appname,
                )
            else:
                # Use standard TCP handler (lazy loading for compatibility)
                print(f"  Creating plain TCP logstash handler (timeout={timeout}s)")
                handler_class = load_class_from_string("logstash.TCPLogstashHandler")
                
                # Try to create handler with timeout, fall back without it if not supported
                try:
                    handler = handler_class(
                        host,
                        port,
                        version=1,
                        timeout=timeout
                    )
                except TypeError:
                    # Older version doesn't support timeout parameter
                    print(f"    Note: python-logstash version doesn't support timeout parameter")
                    handler = handler_class(
                        host,
                        port,
                        version=1
                    )
                
                # Use python-logstash's built-in formatter
                LogstashFormatterVersion1 = load_class_from_string("logstash.formatter.LogstashFormatterVersion1")
                formatter = LogstashFormatterVersion1(
                    message_type='python-logstash',
                    tags=[enable_logstash_conf.customer, enable_logstash_conf.environment, enable_logstash_conf.appname],
                    fqdn=False
                )
                handler.setFormatter(formatter)
                
                # Note: Plain TCP handler doesn't support explicit fields
                print(f"    Note: Using plain TCP - explicit fields not available (use SSL for explicit fields)")
            
            handler.setLevel(get_loglevel_from_str(loglev))
            handler.addFilter(HealthProbeFilter())
            handler.addFilter(UvicornAccessFieldsFilter())
            print(f"  ✓ Logstash handler created for {host}:{port}")
            print(f"    Tags: {enable_logstash_conf.customer}, {enable_logstash_conf.environment}, {enable_logstash_conf.appname}")
            if ssl_enabled:
                print(f"    Explicit fields: customer={enable_logstash_conf.customer}, environment={enable_logstash_conf.environment}, appname={enable_logstash_conf.appname}")
            return handler
        except Exception as e:
            print(f"  ✗ Failed to create Logstash handler for {host}:{port}: {e}")
            print(f"    Logging will continue without Logstash.")
            return None

    def create_file_handler()-> TimedRotatingFileHandler:
        try:
            os.makedirs('./logs', exist_ok=True)
        except:
            pass
        filelogger = TimedRotatingFileHandler('./logs/' + servicetag + '.log', 'midnight', 1)
        filelogger.setLevel(file_level)
        formatter_file = logging.Formatter(get_logfile_format(servicetag))
        filelogger.setFormatter(formatter_file)
        filelogger.addFilter(HealthProbeFilter())
        return filelogger

    def valid_handlers(handlers_with_possible_none: list[Optional[logging.Handler]]) -> list[logging.Handler]:
        return [h for h in handlers_with_possible_none if h is not None]

    file_handler = create_file_handler()
    console_handler = create_console_handler()
    tcp_handler = create_tcp_handler(enable_logstash_conf.host, enable_logstash_conf.port) if enable_logstash_conf is not None else None
    if tcp_handler is not None:
        # Queue in front of the (potentially slow/blocking) network handler so
        # application threads — including the uvicorn event loop — only ever
        # enqueue; all Logstash socket I/O runs on the listener thread.
        tcp_handler = create_tcp_handler_queued(tcp_handler)
    else:
        _stop_active_queue_listener()
    print(f"file_handler: {file_handler}")
    print(f"console_handler: {console_handler}")
    print(f"tcp_handler: {tcp_handler}")
    logging.basicConfig(force=True, level=min(console_level, file_level), handlers=valid_handlers([console_handler, file_handler, tcp_handler]))

# Just to make setup simpler with some standardized env names
def create_logstash_from_environment():
    env=environ.Env()
    enabled = False if "LOGSTASH_ENABLED" not in env else env.str("LOGSTASH_ENABLED").upper() == "TRUE"
    print(f"Logstash enabled: {enabled}")
    if enabled:
        host = None if "LOGSTASH_HOST" not in env else env.str("LOGSTASH_HOST")
        port = None if "LOGSTASH_PORT" not in env else env.int("LOGSTASH_PORT")
        if host is not None and port is not None:
            cust_name = "" if "LOGSTASH_CLIENT_CUSTOMER" not in env else env.str("LOGSTASH_CLIENT_CUSTOMER")
            app_name = "" if "LOGSTASH_CLIENT_APP" not in env else env.str("LOGSTASH_CLIENT_APP")
            env_name = "" if "LOGSTASH_CLIENT_ENVIRONMENT" not in env else env.str("LOGSTASH_CLIENT_ENVIRONMENT")
            return LogstashConfig(host, port, cust_name, env_name, app_name)
        else:
            return None
    else:
        return None