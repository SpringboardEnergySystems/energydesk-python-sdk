# Summary: OIDC Authentication with ETRM Role Authorization

## What Was Changed

### 1. Fixed Import Statement
**File**: `energydeskapi/auth/auth_fastapi.py`
- Changed: `from energydeskapi.auth.auth import authorize_user_etrm`
- To: `from energydeskapi.auth.etrm_authorize import authorize_user_etrm`

### 2. Updated `get_current_user_role()` Method
**File**: `energydeskapi/auth/auth_fastapi.py`

**Key Changes**:
- ✅ Removed Django-only restriction
- ✅ Now works for ALL OAuth providers (Azure, Google, Django)
- ✅ Returns provider information in the response
- ✅ Improved error handling and logging

**Before**:
```python
# Only worked for Django provider
if user.get('provider') != 'django':
    logger.warning("ETRM role lookup only available for Django provider")
    return None
```

**After**:
```python
# Works for all providers
role_pk, role_name = authorize_user_etrm(token)
if role_pk is None or role_name is None:
    logger.warning(f"No ETRM role found for user {user.get('email')} (provider: {user.get('provider')})")
    return None
```

### 3. Access Token Already Stored
**File**: `energydeskapi/auth/auth_fastapi.py` (line 589)
- The access token is already being stored in the session during OAuth callback
- No additional changes needed here

## How It Works Now

### Authentication Flow (Multi-Provider)
1. User can authenticate via:
   - Azure AD
   - Google
   - Django OAuth
2. After successful authentication:
   - User info stored in session
   - **Access token stored in session** (`access_token` key)
   - User redirected to application

### Authorization Flow (ETRM Backend)
1. When `get_current_user_role()` is called:
   - Retrieves user from session
   - Extracts `access_token` from user session
   - Calls `authorize_user_etrm(token)`
2. The `authorize_user_etrm()` function:
   - Validates the token with Django OAuth backend
   - Looks up user email in ETRM database
   - Returns `(role_pk, role_name)` tuple
3. Result returned with additional context:
   ```python
   {
       'role_pk': 123,
       'role_name': 'admin',
       'email': 'user@example.com',
       'provider': 'azure'  # or 'google' or 'django'
   }
   ```

## Key Points

✅ **Backend authenticates Django but authorizes all providers**
   - The Django OAuth backend validates tokens from all providers
   - User lookup is done by email in the ETRM database
   
✅ **Token is stored in session**
   - No need to pass tokens in headers or cookies
   - Session middleware handles security
   
✅ **Works for all OAuth providers**
   - Azure AD users get ETRM roles
   - Google users get ETRM roles
   - Django users get ETRM roles
   
✅ **Role is optional**
   - User can be authenticated without having a role
   - `get_current_user_role()` returns `None` if no role found
   
## Usage in Your Application

### Option 1: Use the dependency directly
```python
from fastapi import Depends, Request

@app.get("/api/protected")
async def my_route(
    request: Request,
    role_info: Optional[Dict] = Depends(
        lambda r: oidc_auth.get_current_user_role(r)
    )
):
    if not role_info:
        return {"error": "No role assigned"}
    
    return {
        "role": role_info.get('role_name'),
        "provider": role_info.get('provider')
    }
```

### Option 2: Call authorize_user_etrm manually
```python
from energydeskapi.auth.etrm_authorize import authorize_user_etrm

@app.get("/api/my-role")
async def get_role(request: Request):
    user = oidc_auth.get_current_user(request)
    token = user.get('access_token')
    
    role_pk, role_name = authorize_user_etrm(token)
    
    return {"role_pk": role_pk, "role_name": role_name}
```

## Files Created

1. **Example Code**: `energydeskapi/examples/using_oidc_role.py`
   - Complete working example
   - Shows all usage patterns
   - Ready to run and test

2. **Documentation**: `energydeskapi/auth/README_OIDC_ROLES.md`
   - Complete guide to OIDC authentication
   - Setup instructions
   - Usage examples
   - Troubleshooting tips

## Testing

To test the changes:

```bash
# Set environment variables
export DJANGO_OAUTH_CLIENT_ID="your-client-id"
export DJANGO_OAUTH_CLIENT_SECRET="your-client-secret"
export DJANGO_OAUTH_BASE_URL="https://hafslund-uat.energydesk.no/appserver"
export ENERGYDESK_URL="https://hafslund-uat.energydesk.no/appserver"

# Run the example
python energydeskapi/examples/using_oidc_role.py

# Visit in browser
# http://localhost:8000/api/me         - Get current user
# http://localhost:8000/api/me/role    - Get ETRM role
# http://localhost:8000/auth/login     - Login page
```

## Summary

✅ **Fixed** import statement to use correct module path
✅ **Removed** Django-only restriction from `get_current_user_role()`
✅ **Updated** to work with all OAuth providers (Azure, Google, Django)
✅ **Improved** error handling and logging
✅ **Created** comprehensive documentation and examples
✅ **Verified** access token is stored in session correctly

The system now correctly:
1. Authenticates users via multiple OAuth providers
2. Stores their access token in the session
3. Uses that token to authorize with the ETRM backend
4. Returns role information for users from ANY provider

