# SDK Logging with SSL and Explicit Fields

## Overview
The `energydeskapi.sdk.logging_utils` module now supports SSL/TLS encrypted logging with explicit fields (customer, environment, appname) for easy Kibana filtering.

## Features

✅ **SSL/TLS Encryption** - Secure log transmission to logstash  
✅ **Explicit Fields** - customer, environment, appname as top-level fields  
✅ **Lazy Loading** - Falls back gracefully if logstash library unavailable  
✅ **Configurable** - All settings via environment variables  
✅ **Compatible** - Works with existing code, no changes needed  

## Environment Variables

### Required for Logstash
```bash
LOGSTASH_ENABLED=True                   # Enable/disable logstash
LOGSTASH_HOST=elk.energydesk.no         # Logstash server hostname
LOGSTASH_PORT=5000                      # Logstash server port
LOGSTASH_CLIENT_CUSTOMER=CUST1          # Customer identifier
LOGSTASH_CLIENT_ENVIRONMENT=DEV1        # Environment identifier
LOGSTASH_CLIENT_APP=MYAPP               # Application name
```

### Optional Configuration
```bash
LOGSTASH_SSL_ENABLE=true                # Enable SSL/TLS (default: true)
LOGSTASH_SSL_VERIFY=false               # Verify SSL certificates (default: false)
LOGSTASH_TIMEOUT=3                      # Connection timeout in seconds (default: 3)
LOGSTASH_LOGLEVEL=INFO                  # Handler log level (default: INFO)
```

## Usage

### Basic Setup
```python
from energydeskapi.sdk.logging_utils import setup_service_logging, create_logstash_from_environment
import logging

# Create logstash config from environment
logstash_conf = create_logstash_from_environment()

# Setup logging
setup_service_logging(
    servicetag="myapp",
    file_level=logging.INFO,
    console_level=logging.INFO,
    enable_logstash_conf=logstash_conf
)

# Use logging normally
logger = logging.getLogger(__name__)
logger.info("Application started")
```

### What Gets Sent to Logstash

Every log message includes:
```json
{
  "@timestamp": "2026-03-27T19:12:15.319Z",
  "customer": "CUST1",          ← Explicit field
  "environment": "DEV1",        ← Explicit field
  "appname": "MYAPP",           ← Explicit field
  "message": "Application started",
  "level": "INFO",
  "logger_name": "mymodule",
  "tags": ["CUST1", "DEV1", "MYAPP"],
  ...
}
```

## Kibana Filtering

### Simple Queries
```
customer:"CUST1"                    # All logs for customer
environment:"DEV1"                  # All logs for environment
appname:"MYAPP"                     # All logs for application
```

### Combined Queries
```
customer:"CUST1" AND environment:"PROD" AND level:"ERROR"
customer:"CUST1" AND message:*exception*
appname:"MYAPP" AND (environment:"DEV" OR environment:"PROD")
```

## SSL Configuration

### Secure Production Setup
```bash
LOGSTASH_ENABLED=True
LOGSTASH_HOST=elk.company.com
LOGSTASH_PORT=5000
LOGSTASH_SSL_ENABLE=true
LOGSTASH_SSL_VERIFY=true           # Verify certificates
LOGSTASH_CLIENT_CUSTOMER=ACME
LOGSTASH_CLIENT_ENVIRONMENT=PROD
LOGSTASH_CLIENT_APP=WEBAPI
```

### Development Setup (Self-Signed Certs)
```bash
LOGSTASH_ENABLED=True
LOGSTASH_HOST=elk.dev.local
LOGSTASH_PORT=5000
LOGSTASH_SSL_ENABLE=true
LOGSTASH_SSL_VERIFY=false          # Skip verification for self-signed
LOGSTASH_CLIENT_CUSTOMER=TESTCUST
LOGSTASH_CLIENT_ENVIRONMENT=DEV
LOGSTASH_CLIENT_APP=TESTAPP
```

### Plain TCP (No SSL)
```bash
LOGSTASH_ENABLED=True
LOGSTASH_HOST=elk.local
LOGSTASH_PORT=5000
LOGSTASH_SSL_ENABLE=false          # Disable SSL
LOGSTASH_CLIENT_CUSTOMER=CUST1
LOGSTASH_CLIENT_ENVIRONMENT=DEV
LOGSTASH_CLIENT_APP=MYAPP
```

## Code Examples

### Example 1: Simple Application
```python
#!/usr/bin/env python
import logging
from energydeskapi.sdk.logging_utils import setup_service_logging, create_logstash_from_environment

# Setup logging
logstash_conf = create_logstash_from_environment()
setup_service_logging("myapp", enable_logstash_conf=logstash_conf)

# Use logging
logger = logging.getLogger(__name__)
logger.info("Starting application")
logger.warning("Configuration issue detected")
logger.error("Failed to connect to database")
```

### Example 2: With Extra Fields
```python
import logging

logger = logging.getLogger(__name__)

# Add custom fields for filtering
logger.info(
    "User logged in",
    extra={
        "user_id": 12345,
        "user_email": "user@example.com",
        "ip_address": "192.168.1.1"
    }
)

# Result in Kibana:
# customer: "CUST1"
# environment: "DEV1"
# appname: "MYAPP"
# user_id: 12345
# user_email: "user@example.com"
# ip_address: "192.168.1.1"
```

### Example 3: Multi-Environment
```python
import os
from energydeskapi.sdk.logging_utils import setup_service_logging, LogstashConfig
import logging

# Determine environment
env = os.environ.get('ENVIRONMENT', 'DEV')

# Create appropriate config
if env == 'PROD':
    logstash_conf = LogstashConfig(
        host='elk.prod.company.com',
        port=5000,
        customer='ACME',
        environment='PROD',
        appname='WEBAPI'
    )
else:
    logstash_conf = LogstashConfig(
        host='elk.dev.company.com',
        port=5000,
        customer='ACME',
        environment='DEV',
        appname='WEBAPI'
    )

setup_service_logging("webapi", enable_logstash_conf=logstash_conf)
```

## Lazy Loading

The SDK uses lazy loading for the standard `python-logstash` library:

```python
# This won't fail if python-logstash is not installed
handler_class = load_class_from_string("logstash.TCPLogstashHandler")
```

Benefits:
- ✅ SDK works even if `python-logstash` not installed
- ✅ SSL handler is built-in (no external dependency)
- ✅ Falls back gracefully if SSL not available
- ✅ Logging continues to file/console if logstash fails

## Handler Selection

The `create_tcp_handler` function automatically selects the appropriate handler:

| SSL Setting | Handler Used | Dependencies |
|-------------|--------------|--------------|
| `SSL_ENABLE=true` | `SSLTCPLogstashHandler` | Built-in (no external deps) |
| `SSL_ENABLE=false` | `TCPLogstashHandler` | Requires `python-logstash` |

## Error Handling

If logstash handler creation fails:
1. Error is logged/printed
2. Handler returns `None`
3. Logging continues to console and file
4. Application keeps running

Example output:
```
✗ Failed to create Logstash handler for elk.server.com:5000: Connection refused
  Logging will continue without Logstash.
```

## Testing

### Test Script
```bash
cd /path/to/sdk
python test_sdk_logging.py
```

### Manual Test
```python
from energydeskapi.sdk.logging_utils import setup_service_logging, LogstashConfig
import logging

# Test with explicit config
conf = LogstashConfig(
    host='elk.energydesk.no',
    port=5000,
    customer='TEST',
    environment='DEV',
    appname='TEST'
)

setup_service_logging("test", enable_logstash_conf=conf)

logger = logging.getLogger(__name__)
logger.info("TEST: Verify this appears in Kibana")
```

Then search Kibana for: `customer:"TEST" AND message:*TEST*`

## Troubleshooting

### Handler Not Created
**Symptom:** `tcp_handler: None`

**Possible Causes:**
1. `LOGSTASH_ENABLED=False` or not set
2. `LOGSTASH_HOST` or `LOGSTASH_PORT` not set
3. Connection to logstash server failed
4. SSL library import failed (for SSL mode)
5. `python-logstash` not installed (for plain TCP mode)

**Solution:**
- Check environment variables
- Test connection: `telnet elk.server.com 5000`
- Check logs for specific error message

### Messages Not Appearing in Kibana
**Symptom:** Handler created but logs don't appear

**Check:**
1. Logstash server is running
2. Port 5000 is open/accessible
3. SSL settings match server (enable/disable)
4. Certificate issues (try `SSL_VERIFY=false`)
5. Check Kibana index pattern refresh

### SSL Certificate Errors
**Symptom:** SSL handshake failures

**Solution:**
```bash
# For self-signed certificates
LOGSTASH_SSL_VERIFY=false

# For proper certificates
LOGSTASH_SSL_VERIFY=true
```

## Migration from Old SDK

### Old Code (No SSL, No Explicit Fields)
```python
# Old setup - tags only
setup_service_logging("myapp", enable_logstash_conf=conf)
# Logs: tags=["CUST1", "DEV1", "MYAPP"]
```

### New Code (SSL + Explicit Fields)
```python
# New setup - automatic SSL + explicit fields
setup_service_logging("myapp", enable_logstash_conf=conf)
# Logs: customer="CUST1", environment="DEV1", appname="MYAPP"
#       tags=["CUST1", "DEV1", "MYAPP"]
```

**No code changes needed!** Just update environment variables:
```bash
LOGSTASH_SSL_ENABLE=true
LOGSTASH_SSL_VERIFY=false
```

## Summary

The SDK now provides:
- ✅ **SSL/TLS encryption** for secure log transmission
- ✅ **Explicit fields** (customer, environment, appname) for easy filtering
- ✅ **Lazy loading** for graceful fallback
- ✅ **No code changes** required - just environment variables
- ✅ **Backward compatible** - works with existing code

**Kibana filtering is now trivial:**
```
customer:"CUST1" AND environment:"PROD" AND level:"ERROR"
```

Instead of parsing tags or complex queries!

