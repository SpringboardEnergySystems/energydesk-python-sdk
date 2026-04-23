# Quick Reference: SDK Logging in PODs

## Environment Variables (Set in Pod Config)

```bash
# Required
LOGSTASH_ENABLED=True
LOGSTASH_HOST=elk.energydesk.no
LOGSTASH_PORT=5000
LOGSTASH_CLIENT_CUSTOMER=CUST1
LOGSTASH_CLIENT_ENVIRONMENT=PROD
LOGSTASH_CLIENT_APP=MYAPP

# Optional (SSL defaults to enabled)
LOGSTASH_SSL_ENABLE=true           # Default: true
LOGSTASH_SSL_VERIFY=false          # Default: false
LOGSTASH_TIMEOUT=3                 # Default: 3
LOGSTASH_LOGLEVEL=INFO             # Default: INFO
```

## Python Code (Same for All PODs)

```python
from energydeskapi.sdk.logging_utils import setup_service_logging, create_logstash_from_environment
import logging

# Load config from environment
logstash_conf = create_logstash_from_environment()

# Setup logging
setup_service_logging(
    servicetag="mypod",
    enable_logstash_conf=logstash_conf
)

# Use logging
logger = logging.getLogger(__name__)
logger.info("Application started")
```

## Log Output

Every log includes explicit fields:
```json
{
  "customer": "CUST1",
  "environment": "PROD",
  "appname": "MYAPP",
  "message": "Application started",
  "level": "INFO",
  ...
}
```

## Kibana Search

```
customer:"CUST1"
environment:"PROD"
appname:"MYAPP"
customer:"CUST1" AND level:"ERROR"
```

## Features

✅ SSL/TLS encryption (automatic)  
✅ Explicit fields (automatic)  
✅ Lazy loading (no crashes if deps missing)  
✅ Fallback to file/console if logstash down  

## Test

```bash
cd /path/to/sdk
python test_sdk_logging.py
```

Then search Kibana for test messages.

## Status

✅ Working in Django  
✅ Working in SDK  
✅ Ready for all PODs

