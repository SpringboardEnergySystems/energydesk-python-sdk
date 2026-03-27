#!/usr/bin/env python
"""
Test script to verify SDK logging setup with SSL and explicit fields.
"""
import os
import sys
import environ

# Set up environment variables for testing
os.environ['LOGSTASH_ENABLED'] = 'True'
os.environ['LOGSTASH_HOST'] = 'elk.energydesk.no'
os.environ['LOGSTASH_PORT'] = '5000'
os.environ['LOGSTASH_SSL_ENABLE'] = 'true'
os.environ['LOGSTASH_SSL_VERIFY'] = 'false'
os.environ['LOGSTASH_TIMEOUT'] = '3'
os.environ['LOGSTASH_LOGLEVEL'] = 'INFO'
os.environ['LOGSTASH_CLIENT_CUSTOMER'] = 'TEST_CUST'
os.environ['LOGSTASH_CLIENT_ENVIRONMENT'] = 'TEST_ENV'
os.environ['LOGSTASH_CLIENT_APP'] = 'SDK_TEST'

# Add SDK to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from energydeskapi.sdk.logging_utils import setup_service_logging, create_logstash_from_environment
import logging

print("=" * 70)
print("SDK LOGGING SETUP TEST")
print("=" * 70)

# Create logstash config from environment
logstash_conf = create_logstash_from_environment()

if logstash_conf:
    print(f"\n✓ Logstash configuration loaded:")
    print(f"  Host: {logstash_conf.host}")
    print(f"  Port: {logstash_conf.port}")
    print(f"  Customer: {logstash_conf.customer}")
    print(f"  Environment: {logstash_conf.environment}")
    print(f"  App Name: {logstash_conf.appname}")
    print()
    
    # Setup logging with SSL handler
    setup_service_logging(
        servicetag="sdk_test",
        file_level=logging.INFO,
        console_level=logging.INFO,
        enable_logstash_conf=logstash_conf
    )
    
    print("\n✓ Logging setup complete!")
    print()
    
    # Test logging
    logger = logging.getLogger(__name__)
    
    print("Sending test log messages...")
    logger.info("TEST: SDK logging with SSL - INFO level")
    logger.warning("TEST: SDK logging with SSL - WARNING level")
    logger.error("TEST: SDK logging with SSL - ERROR level")
    
    print("\n✓ Test messages sent successfully!")
    print()
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print("Check your Kibana for these test messages.")
    print()
    print("Search queries to use in Kibana:")
    print(f'  customer:"{logstash_conf.customer}"')
    print(f'  environment:"{logstash_conf.environment}"')
    print(f'  appname:"{logstash_conf.appname}"')
    print(f'  Combined: customer:"{logstash_conf.customer}" AND message:*TEST*')
    print()
    print("Expected log structure:")
    print('{')
    print(f'  "customer": "{logstash_conf.customer}",')
    print(f'  "environment": "{logstash_conf.environment}",')
    print(f'  "appname": "{logstash_conf.appname}",')
    print('  "message": "TEST: SDK logging with SSL - INFO level",')
    print('  "level": "INFO",')
    print('  ...')
    print('}')
    print()
    print("=" * 70)
    print("✅ SDK logging test complete!")
    print("=" * 70)
else:
    print("\n✗ Logstash configuration not found")
    print("Check environment variables:")
    print("  LOGSTASH_ENABLED, LOGSTASH_HOST, LOGSTASH_PORT")
    print("  LOGSTASH_CLIENT_CUSTOMER, LOGSTASH_CLIENT_ENVIRONMENT, LOGSTASH_CLIENT_APP")

