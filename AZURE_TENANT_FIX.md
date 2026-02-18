# Azure Tenant Configuration Fix

## Problem
When trying to authenticate with Azure AD using the `auth_django.py` library, the following error occurred:

```
AADSTS50194: Application '5accf917-5ec1-4f6b-99e0-10cc6fd952b4'(EnergydeskClearingservices_prod) 
is not configured as a multi-tenant application. Usage of the /common endpoint is not supported 
for such applications created after '10/15/2018'. Use a tenant-specific endpoint or configure 
the application to be multi-tenant.
```

## Root Cause
The `create_auth_from_settings()` function in `auth_django.py` was looking for the environment variable `AZURE_TENANT_ID`, but it was not being set. When the tenant variable was not found, the code defaulted to `'common'`, which caused Azure AD to reject the authentication request since the application is configured as single-tenant.

## Solution
Modified `auth_django.py` (lines 888-902) to implement a fallback mechanism:

1. **First priority**: Check for `AZURE_TENANT_ID` environment variable
2. **Second priority**: If not set, extract the tenant ID from `OIDC_OP_AUTHORIZATION_ENDPOINT` URL
3. **Fallback**: Use `'common'` if neither is available

```python
# Determine Azure tenant: check AZURE_TENANT_ID first, then parse from OIDC_OP_AUTHORIZATION_ENDPOINT
azure_tenant = os.environ.get('AZURE_TENANT_ID')
if not azure_tenant:
    # Try to extract tenant from OIDC_OP_AUTHORIZATION_ENDPOINT
    # Format: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
    auth_endpoint = os.environ.get('OIDC_OP_AUTHORIZATION_ENDPOINT', '')
    if 'login.microsoftonline.com/' in auth_endpoint:
        # Extract tenant ID from URL
        import re
        match = re.search(r'login\.microsoftonline\.com/([^/]+)', auth_endpoint)
        if match:
            azure_tenant = match.group(1)
            print(f"[DEBUG] Extracted Azure tenant from OIDC_OP_AUTHORIZATION_ENDPOINT: {azure_tenant}")

if not azure_tenant:
    azure_tenant = 'common'  # Fallback to 'common' if nothing found
```

This approach makes the code compatible with all existing deployments that already have `OIDC_OP_AUTHORIZATION_ENDPOINT` configured.

## Environment Variables for Azure Authentication

### Option 1: Explicit tenant ID (recommended for new deployments)
```bash
OIDC_RP_CLIENT_ID=5accf917-5ec1-4f6b-99e0-10cc6fd952b4
OIDC_RP_CLIENT_SECRET=<your-secret>
AZURE_TENANT_ID=20d3c681-9982-4395-abd6-7973f7e0f26a
```

### Option 2: Extract from authorization endpoint (compatible with existing deployments)
```bash
OIDC_RP_CLIENT_ID=5accf917-5ec1-4f6b-99e0-10cc6fd952b4
OIDC_RP_CLIENT_SECRET=<your-secret>
OIDC_OP_AUTHORIZATION_ENDPOINT=https://login.microsoftonline.com/20d3c681-9982-4395-abd6-7973f7e0f26a/oauth2/v2.0/authorize
```

The code will automatically extract `20d3c681-9982-4395-abd6-7973f7e0f26a` from the URL.

### Optional
```bash
OIDC_TITLE=Your Application Name
```

## How It Works

1. When `AZURE_TENANT_ID` is explicitly set, it uses that value directly
2. When `AZURE_TENANT_ID` is not set but `OIDC_OP_AUTHORIZATION_ENDPOINT` is configured:
   - Uses regex to extract the tenant ID from the URL pattern: `login.microsoftonline.com/{tenant}/...`
   - Works with the standard Azure AD authorization endpoint format
3. If neither is available, falls back to `'common'` (which will only work for multi-tenant apps)

## Testing
After applying this fix:
1. ✅ The code correctly reads `AZURE_TENANT_ID` when available
2. ✅ The code extracts tenant from `OIDC_OP_AUTHORIZATION_ENDPOINT` when `AZURE_TENANT_ID` is not set
3. ✅ The Azure AD authentication URL uses the tenant-specific endpoint instead of `/common`
4. ✅ Authentication succeeds for single-tenant Azure AD applications
5. ✅ Compatible with all existing deployments that have `OIDC_OP_*` variables configured

## Additional Notes
- The `OIDC_OP_TOKEN_ENDPOINT`, `OIDC_OP_JWKS_ENDPOINT`, and `OIDC_OP_USER_ENDPOINT` variables are NOT used by `auth_django.py` for Azure. The library constructs these URLs automatically from the tenant ID using Azure's well-known configuration endpoint:
  ```
  https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration
  ```
- The debug logging shows whether the tenant was extracted from the URL or used directly
- The regex pattern `login\.microsoftonline\.com/([^/]+)` extracts everything between the domain and the next slash, which captures the tenant ID

