# Django OIDC Authentication

This module provides multi-provider OIDC authentication for Django applications, supporting Azure AD, Google, and Django OAuth Toolkit.

## Installation

1. Install the required dependencies:
```bash
pip install authlib django
```

2. Add to your Django project's `requirements.txt`:
```
energydeskapi
authlib>=1.2.0
```

## Configuration

### 1. Add to Django settings.py

```python
# OIDC Authentication Configuration
OIDC_TITLE = "My Application"

OIDC_PROVIDERS = {
    'azure': {
        'client_id': 'your-azure-client-id',
        'client_secret': 'your-azure-client-secret',
        'tenant': 'your-tenant-id-or-common'
    },
    'google': {
        'client_id': 'your-google-client-id.apps.googleusercontent.com',
        'client_secret': 'your-google-client-secret'
    },
    'django_oauth': {
        'client_id': 'your-django-oauth-client-id',
        'client_secret': 'your-django-oauth-client-secret',
        'base_url': 'https://your-oauth-server.com',
        'authorization_endpoint': '/o/authorize/',
        'token_endpoint': '/o/token/',
        'userinfo_endpoint': '/o/userinfo/',
        'jwks_uri': '/o/.well-known/jwks.json'
    }
}

# Paths that require OIDC authentication
OIDC_PROTECTED_PATHS = ['/portal/', '/api/']

# Paths that are exempt from OIDC (still available without auth)
OIDC_EXEMPT_PATHS = ['/admin/', '/auth/', '/static/', '/media/']

# Add the middleware (optional - for automatic protection)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add OIDC middleware after auth middleware
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',
]

# Ensure sessions are enabled
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # or 'cached_db', 'file', etc.
```

### 2. Add URL patterns to your main urls.py

```python
from django.contrib import admin
from django.urls import path, include
from energydeskapi.auth.auth_django import create_auth_from_settings

# Create auth instance from settings
oidc_auth = create_auth_from_settings()

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include OIDC auth URLs
    path('auth/', include(oidc_auth.get_urls())),
    # Your other URLs
    path('', include('myapp.urls')),
]
```

## Usage

### Option 1: Using Middleware (Automatic Protection)

If you've added `OIDCAuthMiddleware` to your middleware stack, all paths matching `OIDC_PROTECTED_PATHS` will automatically require authentication.

```python
# settings.py
OIDC_PROTECTED_PATHS = ['/portal/', '/api/']
```

Any request to `/portal/` or `/api/` will automatically redirect to login if not authenticated.

### Option 2: Using Decorator (Manual Protection)

Protect individual views with the decorator:

```python
from django.http import HttpResponse
from energydeskapi.auth.auth_django import create_auth_from_settings

# Create auth instance
oidc_auth = create_auth_from_settings()

@oidc_auth.require_auth_decorator
def my_protected_view(request):
    # Access user info from session
    user_info = request.session.get('oidc_user')
    return HttpResponse(f"Hello {user_info['name']}!")
```

### Option 3: Manual Check in Views

```python
from django.shortcuts import redirect
from django.urls import reverse

def my_view(request):
    user_info = request.session.get('oidc_user')
    if not user_info or not user_info.get('authenticated'):
        request.session['oidc_next'] = request.get_full_path()
        return redirect(reverse('oidc_login'))
    
    # User is authenticated
    return HttpResponse(f"Hello {user_info['name']}!")
```

## Available URLs

Once configured, the following URLs are available:

- `/auth/login/` - Provider selection page
- `/auth/login/<provider>/` - Start OAuth flow for specific provider (e.g., `/auth/login/azure/`)
- `/auth/authorize/<provider>/` - OAuth callback URL (configured in your OAuth provider)
- `/auth/logout/` - Logout and clear session
- `/auth/profile/` - Example protected profile page

## User Information

After successful authentication, user information is stored in the session:

```python
user_info = request.session.get('oidc_user')
# {
#     'provider': 'azure',  # or 'google', 'django_oauth'
#     'email': 'user@example.com',
#     'name': 'John Doe',
#     'sub': 'unique-user-id',
#     'authenticated': True
# }
```

Additionally, a Django user is automatically created/updated and logged in:

```python
if request.user.is_authenticated:
    print(request.user.username)  # Will be the user's email
    print(request.user.email)
```

## OAuth Provider Setup

### Azure AD

1. Register an application in Azure Portal
2. Add redirect URI: `https://yourdomain.com/auth/authorize/azure/`
3. Generate a client secret
4. Use the Application (client) ID and Directory (tenant) ID in settings

### Google

1. Create credentials in Google Cloud Console
2. Add authorized redirect URI: `https://yourdomain.com/auth/authorize/google/`
3. Use the Client ID and Client Secret in settings

### Django OAuth Toolkit

1. Create an application in your OAuth server's admin
2. Set redirect URI: `https://yourdomain.com/auth/authorize/django_oauth/`
3. Use the Client ID and Client Secret in settings

## Customization

### Custom Title

```python
from energydeskapi.auth.auth_django import DjangoOIDCAuth

oidc_auth = DjangoOIDCAuth(
    title="My Custom Application",
    config=settings.OIDC_PROVIDERS
)
```

### Custom Redirect After Login

The middleware and views automatically support the `next` parameter:

```python
# Store next URL before redirecting to login
request.session['oidc_next'] = '/custom/redirect/path/'
```

### Accessing User in Templates

```django
{% if request.user.is_authenticated %}
    <p>Welcome, {{ request.user.username }}!</p>
    <p>Email: {{ request.session.oidc_user.email }}</p>
    <p>Provider: {{ request.session.oidc_user.provider }}</p>
    <a href="{% url 'oidc_logout' %}">Logout</a>
{% else %}
    <a href="{% url 'oidc_login' %}">Login</a>
{% endif %}
```

## Security Considerations

1. **Use HTTPS in production** - OAuth requires secure connections
2. **Set secure session cookies** in settings.py:
   ```python
   SESSION_COOKIE_SECURE = True  # Only send over HTTPS
   SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
   SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
   ```
3. **Keep secrets secure** - Use environment variables:
   ```python
   import os
   OIDC_PROVIDERS = {
       'azure': {
           'client_id': os.environ.get('AZURE_CLIENT_ID'),
           'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
           'tenant': os.environ.get('AZURE_TENANT_ID'),
       }
   }
   ```

## Troubleshooting

### Redirect URI Mismatch

Make sure the redirect URI in your OAuth provider exactly matches:
`https://yourdomain.com/auth/authorize/<provider>/`

### Session Not Persisting

Ensure sessions are properly configured in Django:
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
python manage.py migrate  # Create session tables
```

### Behind a Reverse Proxy

If running behind nginx/Apache, ensure proper headers are set:
```python
# settings.py
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Example: Complete Django Project Setup

```python
# settings.py
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your apps
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',
]

# OIDC Configuration
OIDC_TITLE = "My Portal"
OIDC_PROVIDERS = {
    'azure': {
        'client_id': os.environ.get('AZURE_CLIENT_ID'),
        'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
        'tenant': os.environ.get('AZURE_TENANT_ID', 'common'),
    }
}
OIDC_PROTECTED_PATHS = ['/portal/']
OIDC_EXEMPT_PATHS = ['/admin/', '/auth/', '/static/']

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# urls.py
from django.contrib import admin
from django.urls import path, include
from energydeskapi.auth.auth_django import create_auth_from_settings

oidc_auth = create_auth_from_settings()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(oidc_auth.get_urls())),
    path('portal/', include('myapp.urls')),
]

# myapp/views.py
from django.http import HttpResponse

def portal_home(request):
    # Automatically protected by middleware
    user_info = request.session.get('oidc_user')
    return HttpResponse(f"Welcome to the portal, {user_info['name']}!")
```

## Comparison with FastAPI Version

| Feature | FastAPI (`auth_fastapi.py`) | Django (`auth_django.py`) |
|---------|----------------------------|---------------------------|
| Framework | FastAPI + Starlette | Django |
| Session | SessionMiddleware | Django sessions |
| User creation | Manual | Automatic (Django User model) |
| Protection | Dependency injection | Middleware or decorator |
| URLs | Manual registration | `get_urls()` method |
| Configuration | Constructor params | Django settings |

Both versions share the same OAuth provider support and similar UI/UX.
