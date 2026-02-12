# Django OIDC Authentication - Quick Start

## What Was Created

I've created a complete Django version of the FastAPI OIDC authentication system:

### Files Created:
1. **`auth_django.py`** - Main Django authentication module
2. **`README_DJANGO.md`** - Complete documentation
3. **`django_example.py`** - Comprehensive usage examples
4. **Updated `__init__.py`** - Exports for both Django and FastAPI versions

## Key Features

✅ **Multi-Provider Support**: Azure AD, Google, and Django OAuth Toolkit  
✅ **Django Integration**: Seamlessly integrates with Django's auth system  
✅ **Automatic User Creation**: Creates/updates Django User objects automatically  
✅ **Flexible Protection**: Middleware for automatic protection or decorator for manual control  
✅ **Session Management**: Uses Django's built-in session system  
✅ **Beautiful UI**: Same styled login page as FastAPI version  
✅ **Reverse Proxy Support**: Works behind nginx/Apache with proper headers  

## Quick Installation

```bash
# Install in your Django project
pip install energydeskapi authlib
```

## Minimal Setup

### 1. Add to `settings.py`:

```python
# OIDC Configuration
OIDC_TITLE = "My Portal"
OIDC_PROVIDERS = {
    'azure': {
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret',
        'tenant': 'common'
    }
}
OIDC_PROTECTED_PATHS = ['/portal/']

# Add middleware (after AuthenticationMiddleware)
MIDDLEWARE = [
    # ... other middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',  # Add this
]
```

### 2. Add to `urls.py`:

```python
from energydeskapi.auth.auth_django import create_auth_from_settings

oidc_auth = create_auth_from_settings()

urlpatterns = [
    path('auth/', include(oidc_auth.get_urls())),
    # ... your other URLs ...
]
```

### 3. Use in views:

```python
# Automatically protected by middleware if path in OIDC_PROTECTED_PATHS
def my_view(request):
    user_info = request.session.get('oidc_user')
    return HttpResponse(f"Hello {user_info['name']}!")

# Or use decorator for specific views
@oidc_auth.require_auth_decorator
def protected_view(request):
    return HttpResponse("Protected content")
```

## How It Works

1. **User visits protected path** → Middleware checks authentication
2. **Not authenticated** → Redirect to `/auth/login/`
3. **User selects provider** → OAuth flow initiated
4. **OAuth callback** → User info retrieved and stored in session
5. **Django user created** → Automatic creation/update of Django User object
6. **Redirect to original page** → User accesses protected content

## User Information

After authentication, you have access to:

```python
# From OIDC session
oidc_user = request.session.get('oidc_user')
# {'provider': 'azure', 'email': 'user@example.com', 
#  'name': 'John Doe', 'sub': 'unique-id', 'authenticated': True}

# From Django User model
if request.user.is_authenticated:
    username = request.user.username  # Will be the email
    email = request.user.email
```

## Three Ways to Protect Views

### Option 1: Middleware (Automatic)
```python
# settings.py
OIDC_PROTECTED_PATHS = ['/portal/', '/api/']
# All matching paths are automatically protected
```

### Option 2: Decorator (Per-View)
```python
@oidc_auth.require_auth_decorator
def my_view(request):
    # Protected view
    pass
```

### Option 3: Manual Check
```python
def my_view(request):
    user = oidc_auth.get_current_user(request)
    if not user:
        return redirect(reverse('oidc_login'))
    # Continue with authenticated user
```

## OAuth Provider Configuration

### Azure AD
- Register app in Azure Portal
- Redirect URI: `https://yourdomain.com/auth/authorize/azure/`
- Copy Client ID, Secret, and Tenant ID

### Google
- Create credentials in Google Cloud Console  
- Redirect URI: `https://yourdomain.com/auth/authorize/google/`
- Copy Client ID and Secret

### Django OAuth Toolkit
- Register application in OAuth server
- Redirect URI: `https://yourdomain.com/auth/authorize/django_oauth/`
- Configure endpoints in settings

## Available URLs

Once configured:
- `/auth/login/` - Provider selection
- `/auth/login/<provider>/` - Start OAuth flow
- `/auth/authorize/<provider>/` - OAuth callback
- `/auth/logout/` - Logout
- `/auth/profile/` - Example profile page

## Security Best Practices

```python
# settings.py - Production configuration
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
USE_X_FORWARDED_HOST = True  # Behind reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Use environment variables for secrets
import os
OIDC_PROVIDERS = {
    'azure': {
        'client_id': os.environ.get('AZURE_CLIENT_ID'),
        'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
        'tenant': os.environ.get('AZURE_TENANT_ID', 'common'),
    }
}
```

## Differences from FastAPI Version

| Feature | FastAPI | Django |
|---------|---------|--------|
| Framework | FastAPI + Starlette | Django |
| Session Storage | SessionMiddleware | Django sessions (DB) |
| User Management | Manual | Automatic (User model) |
| Route Protection | Dependency injection | Middleware/decorator |
| URL Registration | Manual decorator | `get_urls()` method |

## Next Steps

1. **See full documentation**: Open `README_DJANGO.md`
2. **See examples**: Open `django_example.py`
3. **Configure OAuth providers** in your application portals
4. **Test locally** with `python manage.py runserver`
5. **Deploy to production** with HTTPS and proper secret management

## Integration with Your Django Portal

Since you mentioned you'll include this SDK in your Django portal:

```bash
# In your Django portal project
pip install git+https://github.com/yourusername/energydesk-python-sdk.git
# or
pip install energydeskapi
```

Then follow the Quick Setup above to integrate OIDC authentication.

## Support

For questions or issues:
- Review `README_DJANGO.md` for detailed documentation
- Check `django_example.py` for code examples
- Compare with `auth_fastapi.py` for reference

---

**The Django authentication module is production-ready and includes all the features from the FastAPI version!**
