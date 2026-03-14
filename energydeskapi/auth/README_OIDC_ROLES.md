# OIDC Authentication with ETRM Role Authorization

## Overview

This authentication system provides:
1. **Authentication**: Users can sign in via Azure AD, Google, or Django OAuth
2. **Authorization**: All authenticated users (regardless of provider) can be authorized via the ETRM backend
3. **Role-based Access**: Get user's role information from ETRM database for access control

## How It Works

### Authentication Flow
```
User → Clicks Login → Redirects to OAuth Provider → User Authenticates 
→ Redirects back with token → Token stored in session → User authenticated
```

### Authorization Flow (ETRM Roles)
```
Authenticated User → Request with token → Backend validates token 
→ Looks up user email in ETRM database → Returns role_pk and role_name
```

**Important**: The backend authenticates using Django OAuth but authorizes ALL providers by looking up the user's email in the ETRM user database.

## Setup

### 1. Environment Variables

Set these in your `.env` file:

```bash
# Django OAuth (used for authentication)
DJANGO_OAUTH_CLIENT_ID="your-client-id"
DJANGO_OAUTH_CLIENT_SECRET="your-client-secret"
DJANGO_OAUTH_BASE_URL="https://your-domain.energydesk.no/appserver"

# ETRM Backend (used for authorization)
ENERGYDESK_URL="https://your-domain.energydesk.no/appserver"

# Optional: Other OAuth providers
AZURE_OAUTH_CLIENT_ID="..."
AZURE_OAUTH_CLIENT_SECRET="..."
AZURE_OAUTH_TENANT_ID="..."

GOOGLE_OAUTH_CLIENT_ID="..."
GOOGLE_OAUTH_CLIENT_SECRET="..."
```

### 2. Initialize OIDC in Your FastAPI App

```python
from fastapi import FastAPI
from energydeskapi.auth.auth_fastapi import create_auth_from_env

app = FastAPI(title="My App")

# Create OIDC auth from environment
oidc_auth = create_auth_from_env(
    title="My Application",
    app=app,
    secret_key="your-secret-key-here",  # Used for session encryption
    allow_guest=False  # Set to True to allow unauthenticated access
)
```

## Usage Examples

### Example 1: Get Current User (Basic Info)

```python
from fastapi import Depends, Request
from typing import Optional, Dict, Any

@app.get("/api/me")
async def get_me(
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(
        lambda r: oidc_auth.optional_auth(r) if oidc_auth else None
    )
):
    if not user:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "provider": user.get('provider'),  # azure, google, or django
        "email": user.get('email'),
        "name": user.get('name'),
        "sub": user.get('sub')
    }
```

### Example 2: Get ETRM Role Information

```python
@app.get("/api/me/role")
async def get_my_role(
    request: Request,
    role_info: Optional[Dict[str, Any]] = Depends(
        lambda r: oidc_auth.get_current_user_role(r) if oidc_auth else None
    )
):
    """
    Get ETRM role - works for ALL OAuth providers
    """
    if not role_info:
        return {
            "error": "No role assigned in ETRM system"
        }
    
    return {
        "role_pk": role_info.get('role_pk'),
        "role_name": role_info.get('role_name'),
        "email": role_info.get('email'),
        "provider": role_info.get('provider')
    }
```

### Example 3: Protected Route (Requires Authentication)

```python
@app.get("/api/protected")
async def protected_route(
    request: Request,
    user: Dict[str, Any] = Depends(
        lambda r: oidc_auth.require_auth(r) if oidc_auth else {}
    )
):
    """
    Returns 401 if user is not authenticated
    """
    return {
        "message": "Secret data",
        "user": user.get('email')
    }
```

### Example 4: Role-Based Access Control

```python
@app.get("/api/admin-only")
async def admin_only(
    request: Request,
    user: Dict[str, Any] = Depends(
        lambda r: oidc_auth.require_auth(r) if oidc_auth else {}
    ),
    role_info: Optional[Dict[str, Any]] = Depends(
        lambda r: oidc_auth.get_current_user_role(r) if oidc_auth else None
    )
):
    if not role_info:
        raise HTTPException(status_code=403, detail="No role assigned")
    
    # Check for admin role
    if role_info.get('role_name') not in ['admin', 'superuser']:
        raise HTTPException(
            status_code=403,
            detail=f"Admin role required. Your role: {role_info.get('role_name')}"
        )
    
    return {"message": "Welcome, admin!"}
```

### Example 5: Manual Token Validation

If you need to call `authorize_user_etrm` directly:

```python
from energydeskapi.auth.etrm_authorize import authorize_user_etrm

@app.get("/api/validate-token")
async def validate_token(request: Request):
    # Get user from session
    user = oidc_auth.get_current_user(request)
    if not user:
        return {"error": "Not authenticated"}
    
    # Get token
    token = user.get('access_token')
    if not token:
        return {"error": "No token"}
    
    try:
        # Call authorization directly
        role_pk, role_name = authorize_user_etrm(token)
        
        return {
            "role_pk": role_pk,
            "role_name": role_name,
            "email": user.get('email')
        }
    except Exception as e:
        return {"error": str(e)}
```

## Token Storage

When a user authenticates, the following is stored in their session:

```python
request.session['user'] = {
    'provider': 'azure',  # or 'google', 'django'
    'email': 'user@example.com',
    'name': 'John Doe',
    'sub': 'unique-user-id',
    'authenticated': True,
    'access_token': 'eyJhbG...'  # OAuth access token
}
```

The `access_token` is used by `authorize_user_etrm()` to:
1. Validate the token with the Django OAuth backend
2. Look up the user's email in the ETRM database
3. Return their role information

## Authentication vs Authorization

### Authentication (OAuth)
- **Purpose**: Verify user identity
- **Providers**: Azure AD, Google, Django
- **Result**: User email, name, and access token
- **Scope**: Confirms "you are who you say you are"

### Authorization (ETRM)
- **Purpose**: Determine user permissions
- **Backend**: Django ETRM database
- **Result**: Role PK and role name
- **Scope**: Determines "what you're allowed to do"

## Key Points

1. **All providers work**: Users authenticated via Azure, Google, or Django can all be authorized via ETRM
2. **Email-based lookup**: The ETRM backend uses the user's email to look up their role
3. **Token required**: The access token from OAuth is passed to the ETRM backend for validation
4. **Role optional**: A user can be authenticated without having a role assigned in ETRM
5. **Session-based**: The token is stored in the session, not in cookies or headers

## Troubleshooting

### "No access token found in user session"
- User's session doesn't contain an access token
- User may need to log out and log back in

### "No role information available"
- User is authenticated but has no role in ETRM database
- Check that the user's email exists in the ETRM user table
- Verify the email matches exactly (case-sensitive)

### "Failed to get role information"
- Network error connecting to ETRM backend
- Check `ENERGYDESK_URL` environment variable
- Verify the token is valid

## Testing

See the example file for a complete working example:
```bash
python energydeskapi/examples/using_oidc_role.py
```

Then visit:
- `http://localhost:8000/api/me` - See current user info
- `http://localhost:8000/api/me/role` - See role information
- `http://localhost:8000/auth/login` - Login page

## Security Notes

1. **Session security**: Use a strong `secret_key` for session encryption
2. **HTTPS required**: Always use HTTPS in production
3. **Token expiry**: OAuth tokens expire - handle token refresh if needed
4. **Role caching**: Role info is fetched on each request - consider caching if performance is critical

