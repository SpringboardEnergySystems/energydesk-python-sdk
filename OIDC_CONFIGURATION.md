# OIDC Authentication Configuration

## Overview

The `energydeskapi.auth.auth_django` module provides multi-provider OIDC authentication for Django applications. The configuration is loaded directly from environment variables to avoid Django app loading issues.

## Supported Providers

1. **Azure AD** (Microsoft)
2. **Google OAuth**
3. **Django OAuth Toolkit** (custom Django OAuth server)

## Environment Variables

### Azure AD Configuration

```bash
export AZURE_CLIENT_ID="your-azure-client-id"
export AZURE_CLIENT_SECRET="your-azure-client-secret"
export AZURE_TENANT_ID="your-tenant-id"  # Optional, defaults to "common"
```

### Google OAuth Configuration

```bash
export GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

### Django OAuth Toolkit Configuration

```bash
export DJANGO_OAUTH_CLIENT_ID="your-django-client-id"
export DJANGO_OAUTH_CLIENT_SECRET="your-django-client-secret"
export DJANGO_OAUTH_BASE_URL="https://your-django-oauth-server.com"
export DJANGO_OAUTH_AUTHORIZATION_ENDPOINT="/o/authorize/"  # Optional
export DJANGO_OAUTH_TOKEN_ENDPOINT="/o/token/"  # Optional
export DJANGO_OAUTH_USERINFO_ENDPOINT="/oauth_edesk/userinfo/"  # Optional
export DJANGO_OAUTH_JWKS_URI="/o/.well-known/jwks.json"  # Optional
```

### Optional Configuration

```bash
export OIDC_TITLE="My Application Name"  # Displayed on login page
```

## Django Settings Configuration

In your `settings.py` (or `settings/common.py`):

```python
from energydeskapi.auth.auth_django import create_auth_from_settings

# Create OIDC auth instance from environment variables
OIDC_TITLE = "My Energy Portal"
oidc_auth = create_auth_from_settings(title=OIDC_TITLE)

# Store the config for reference (optional)
OIDC_PROVIDERS = oidc_auth.config

# Configure protected paths
OIDC_PROTECTED_PATHS = ['/']  # Protect all paths
OIDC_EXEMPT_PATHS = ['/admin/', '/auth/', '/static/', '/media/']  # Exempt paths
```

## URL Configuration

In your `urls.py`:

```python
from django.urls import path, include
from portal.settings.common import oidc_auth

urlpatterns = [
    # ... other patterns ...
    path('auth/', include(oidc_auth.get_urls())),
]
```

## Middleware (Optional)

To automatically protect paths, add the middleware to your `MIDDLEWARE` in settings:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',
]
```

## How It Works

1. **Environment-Based Configuration**: The `create_auth_from_settings()` function reads configuration directly from environment variables, avoiding the "apps aren't loaded yet" error.

2. **Lazy Imports**: Django models and functions are imported lazily (only when needed) to prevent app loading issues during settings import.

3. **Dynamic Provider Registration**: Only providers with complete configuration (client_id and client_secret) are registered.

## Example .env File

```bash
# Application Settings
OIDC_TITLE="My Energy Portal"

# Google OAuth (if using)
GOOGLE_CLIENT_ID="123456789-abcdefg.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-secret"

# Azure AD (if using)
AZURE_CLIENT_ID="your-azure-client-id"
AZURE_CLIENT_SECRET="your-azure-secret"
AZURE_TENANT_ID="common"

# Django OAuth (if using)
# DJANGO_OAUTH_CLIENT_ID="your-django-client-id"
# DJANGO_OAUTH_CLIENT_SECRET="your-django-secret"
# DJANGO_OAUTH_BASE_URL="https://your-oauth-server.com"
```

## Testing Configuration

To verify your configuration is loaded correctly:

```bash
python << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings.common')

from django.conf import settings
print(f"OIDC Title: {settings.OIDC_TITLE}")
print(f"Configured providers: {list(settings.OIDC_PROVIDERS.keys())}")
EOF
```

## Troubleshooting

### "Apps aren't loaded yet" Error

This error occurs when Django models are imported at the module level in settings. The fix:
- Use `create_auth_from_settings()` which reads directly from environment variables
- Ensure you're using the latest version of the `energydesk-python-sdk` package

### No Providers Showing on Login Page

Check that:
1. Environment variables are set correctly
2. Both `client_id` and `client_secret` are provided for each provider
3. The Django settings are loading the configuration properly

### Provider Not Working

Verify:
1. Redirect URIs are configured correctly in your OAuth provider console
2. The redirect URI format: `https://your-domain.com/auth/authorize/<provider>/`
3. Environment variables match the credentials from your OAuth provider
