# OIDC Configuration Helper Function Update

## Summary

Updated `energydeskapi.auth.auth_fastapi` to provide a configuration helper function similar to the Django version, making it easier to load OIDC configuration from environment variables.

## Changes Made

### 1. SDK Update (`energydeskapi/auth/auth_fastapi.py`)

Added two new helper functions:

#### `get_oidc_config_from_env()` - Config Dictionary Builder
Returns a configuration dictionary from environment variables that can be passed to `FastAPIOIDCAuth`.

**Environment Variables:**
- **Azure AD**: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT` (defaults to 'common')
- **Google**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Django OAuth**: `DJANGO_CLIENT_ID`, `DJANGO_CLIENT_SECRET`, `DJANGO_BASE_URL`
  - Optional: `DJANGO_AUTHORIZATION_ENDPOINT`, `DJANGO_TOKEN_ENDPOINT`, `DJANGO_USERINFO_ENDPOINT`, `DJANGO_JWKS_URI`

**Usage Example:**
```python
from energydeskapi.auth.auth_fastapi import get_oidc_config_from_env, FastAPIOIDCAuth

oidc_config = get_oidc_config_from_env()
if oidc_config:
    oidc_auth = FastAPIOIDCAuth("My App", app, oidc_config, secret_key=secret_key)
```

#### `create_auth_from_env()` - All-in-One Helper
Convenience function that combines config loading and auth initialization.

**Usage Example:**
```python
from energydeskapi.auth.auth_fastapi import create_auth_from_env

oidc_auth = create_auth_from_env("My App", app, secret_key="your-secret-key")
if oidc_auth:
    logger.info("OIDC authentication enabled")
```

### 2. Flex Gateway Update (`flexgateway/server.py`)

Simplified OIDC configuration loading by using the new SDK helper function.

**Before:**
```python
oidc_config = {}

# Azure AD configuration
azure_client_id = get_environment_value("AZURE_CLIENT_ID", "")
if azure_client_id:
    oidc_config['azure'] = {
        'client_id': azure_client_id,
        'client_secret': get_environment_value("AZURE_CLIENT_SECRET", ""),
        'tenant': get_environment_value("AZURE_TENANT", "common")
    }

# Google configuration
google_client_id = get_environment_value("GOOGLE_CLIENT_ID", "")
if google_client_id:
    oidc_config['google'] = {
        'client_id': google_client_id,
        'client_secret': get_environment_value("GOOGLE_CLIENT_SECRET", "")
    }

# Django OAuth configuration
django_client_id = get_environment_value("DJANGO_CLIENT_ID", "")
if django_client_id:
    oidc_config['django'] = {
        'client_id': django_client_id,
        'client_secret': get_environment_value("DJANGO_CLIENT_SECRET", ""),
        'base_url': get_environment_value("DJANGO_BASE_URL", ""),
        # ... more config
    }
```

**After:**
```python
from energydeskapi.auth.auth_fastapi import get_oidc_config_from_env

oidc_config = get_oidc_config_from_env()
```

## Benefits

1. **Consistency**: FastAPI and Django clients now use the same pattern for loading OIDC configuration
2. **Simplicity**: Reduces boilerplate code in applications using the SDK
3. **Maintainability**: Configuration logic is centralized in the SDK
4. **Flexibility**: Applications can still build custom configs if needed, or use the helper

## Migration Guide

For existing FastAPI applications using the SDK:

### Option 1: Use the helper function (recommended)
```python
from energydeskapi.auth.auth_fastapi import get_oidc_config_from_env, FastAPIOIDCAuth

# Replace manual config building with:
oidc_config = get_oidc_config_from_env()

if oidc_config:
    oidc_auth = FastAPIOIDCAuth("My App", app, oidc_config, secret_key=secret_key)
```

### Option 2: Use the all-in-one helper
```python
from energydeskapi.auth.auth_fastapi import create_auth_from_env

# Replace entire OIDC setup with:
oidc_auth = create_auth_from_env("My App", app, secret_key=secret_key)
```

## Testing

The updated code maintains backward compatibility. Existing applications will continue to work without changes, but can be simplified by adopting the new helper functions.

## Related Files

- **SDK**: `energydeskapi/auth/auth_fastapi.py`
- **Flex Gateway**: `flexgateway/server.py`
- **Django Reference**: `energydeskapi/auth/auth_django.py`
