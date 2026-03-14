"""
Example: Using OIDC Authentication with ETRM Role Information

This example demonstrates how to:
1. Set up OIDC authentication with FastAPI
2. Get current authenticated user
3. Retrieve ETRM role information for authenticated users (all providers)
4. Use role information in protected routes

NOTE: The backend authenticates via Django OAuth but authorizes users from
all providers (Azure, Google, Django) by looking up their email in the ETRM database.
"""

from fastapi import FastAPI, Depends, Request
from energydeskapi.auth.auth_fastapi import create_auth_from_env, FastAPIOIDCAuth
from typing import Optional, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="OIDC Role Example")

# Initialize OIDC authentication from environment variables
# Required env vars:
# - DJANGO_OAUTH_CLIENT_ID
# - DJANGO_OAUTH_CLIENT_SECRET
# - DJANGO_OAUTH_BASE_URL (e.g., https://hafslund-uat.energydesk.no/appserver)
# - ENERGYDESK_URL (for authorize_user_etrm)
oidc_auth = create_auth_from_env(
    title="My Application",
    app=app,
    secret_key="your-secret-key-here",
    allow_guest=False
)


# Example 1: Get current user (basic info)
@app.get("/api/me")
async def get_me(
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(lambda r: oidc_auth.optional_auth(r) if oidc_auth else None)
):
    """
    Get basic user information from session

    Returns:
        - provider: The OAuth provider used (azure, google, django)
        - email: User's email
        - name: User's name
        - sub: Subject ID
        - authenticated: True/False
    """
    if not user:
        return {"authenticated": False, "message": "Not authenticated"}

    return {
        "authenticated": True,
        "provider": user.get('provider'),
        "email": user.get('email'),
        "name": user.get('name'),
        "sub": user.get('sub')
    }


# Example 2: Get ETRM role information (works for all OAuth providers)
@app.get("/api/me/role")
async def get_my_role(
    request: Request,
    role_info: Optional[Dict[str, Any]] = Depends(lambda r: oidc_auth.get_current_user_role(r) if oidc_auth else None)
):
    """
    Get ETRM role information for the current user

    This works for users authenticated via ANY provider (Azure, Google, Django).
    The backend looks up the user's email in the ETRM database to get their role.

    Returns:
        - role_pk: Role primary key
        - role_name: Role name
        - email: User's email
        - provider: OAuth provider used for authentication
    """
    if not role_info:
        return {
            "error": "No role information available",
            "message": "User is authenticated but has no ETRM role assigned, or authorization failed"
        }

    return {
        "role_pk": role_info.get('role_pk'),
        "role_name": role_info.get('role_name'),
        "email": role_info.get('email'),
        "provider": role_info.get('provider')
    }


# Example 3: Protected route that requires authentication
@app.get("/api/protected")
async def protected_route(
    request: Request,
    user: Dict[str, Any] = Depends(lambda r: oidc_auth.require_auth(r) if oidc_auth else {})
):
    """
    Example of a route that requires authentication

    Will return 401 if user is not authenticated
    """
    return {
        "message": "This is protected data",
        "user": user.get('email')
    }


# Example 4: Route that checks role and does conditional logic
@app.get("/api/admin-only")
async def admin_only_route(
    request: Request,
    user: Dict[str, Any] = Depends(lambda r: oidc_auth.require_auth(r) if oidc_auth else {}),
    role_info: Optional[Dict[str, Any]] = Depends(lambda r: oidc_auth.get_current_user_role(r) if oidc_auth else None)
):
    """
    Example of a route that requires specific role

    Works for users from any OAuth provider (Azure, Google, Django).
    Checks if user has admin role and returns 403 if not.
    """
    if not role_info:
        return {
            "error": "Forbidden",
            "message": "You don't have an assigned role in the ETRM system."
        }, 403

    # Check if user has admin role (customize this check based on your role names)
    if role_info.get('role_name') not in ['admin', 'superuser']:
        return {
            "error": "Forbidden",
            "message": f"This endpoint requires admin role. Your role: {role_info.get('role_name')}"
        }, 403

    return {
        "message": "Welcome, admin!",
        "role": role_info.get('role_name'),
        "role_pk": role_info.get('role_pk')
    }


# Example 5: Manually call authorize_user_etrm with your own token
@app.get("/api/check-token")
async def check_token_manually(request: Request):
    """
    Example showing how to manually call authorize_user_etrm
    if you have a token from another source
    """
    from energydeskapi.auth.etrm_authorize import authorize_user_etrm

    # Get user from session
    user = oidc_auth.get_current_user(request) if oidc_auth else None
    if not user:
        return {"error": "Not authenticated"}

    # Get token from session
    token = user.get('access_token')
    if not token:
        return {"error": "No access token in session"}

    try:
        # Call authorize_user_etrm directly
        role_pk, role_name = authorize_user_etrm(token)

        return {
            "method": "Manual call to authorize_user_etrm",
            "role_pk": role_pk,
            "role_name": role_name,
            "token_present": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to get role information"
        }


if __name__ == "__main__":
    import uvicorn

    # Make sure to set these environment variables:
    # export DJANGO_OAUTH_CLIENT_ID="your-client-id"
    # export DJANGO_OAUTH_CLIENT_SECRET="your-client-secret"
    # export DJANGO_OAUTH_BASE_URL="https://hafslund-uat.energydesk.no/appserver"
    # export ENERGYDESK_URL="https://hafslund-uat.energydesk.no/appserver"

    uvicorn.run(app, host="0.0.0.0", port=8000)

