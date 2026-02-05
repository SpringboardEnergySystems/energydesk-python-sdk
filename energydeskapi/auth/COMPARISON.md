# FastAPI vs Django OIDC Authentication - Side-by-Side Comparison

## Module Overview

| Aspect | FastAPI (`auth_fastapi.py`) | Django (`auth_django.py`) |
|--------|----------------------------|---------------------------|
| **File Location** | `energydeskapi/auth/auth_fastapi.py` | `energydeskapi/auth/auth_django.py` |
| **Main Class** | `FastAPIOIDCAuth` | `DjangoOIDCAuth` |
| **Dependencies** | FastAPI, Starlette, Authlib | Django, Authlib |
| **Session System** | `SessionMiddleware` (Starlette) | Django's built-in sessions |

## Initialization

### FastAPI
```python
from energydeskapi.auth.auth_fastapi import FastAPIOIDCAuth
from fastapi import FastAPI

app = FastAPI()

auth = FastAPIOIDCAuth(
    title="My Service",
    app=app,
    config={
        'azure': {
            'client_id': '...',
            'client_secret': '...',
            'tenant': 'common'
        }
    },
    secret_key="your-secret-key"
)
```

### Django
```python
# settings.py
OIDC_TITLE = "My Service"
OIDC_PROVIDERS = {
    'azure': {
        'client_id': '...',
        'client_secret': '...',
        'tenant': 'common'
    }
}

# urls.py
from energydeskapi.auth.auth_django import create_auth_from_settings

auth = create_auth_from_settings()

urlpatterns = [
    path('auth/', include(auth.get_urls())),
]
```

## Route/URL Registration

### FastAPI
```python
# Automatic when initialized with app
auth = FastAPIOIDCAuth(title="...", app=app, config=...)

# Routes are automatically registered:
# GET /auth/login
# GET /auth/login/{provider}
# GET /auth/authorize/{provider}
# GET /auth/logout
# GET /auth/profile
```

### Django
```python
# Manual URL inclusion
from django.urls import path, include

urlpatterns = [
    path('auth/', include(auth.get_urls())),
]

# Generates URLs:
# GET /auth/login/ (name='oidc_login')
# GET /auth/login/<provider>/ (name='oidc_login_provider')
# GET /auth/authorize/<provider>/ (name='oidc_authorize')
# GET /auth/logout/ (name='oidc_logout')
# GET /auth/profile/ (name='oidc_profile')
```

## Protecting Views/Endpoints

### FastAPI - Dependency Injection
```python
from fastapi import Depends

# Require authentication
@app.get("/protected")
async def protected_route(user: dict = Depends(auth.require_auth)):
    return {"message": f"Hello {user['name']}"}

# Optional authentication
@app.get("/optional")
async def optional_route(user: dict = Depends(auth.optional_auth)):
    if user:
        return {"message": f"Hello {user['name']}"}
    return {"message": "Hello guest"}

# Manual check
@app.get("/manual")
async def manual_route(request: Request):
    user = auth.get_current_user(request)
    if not user:
        raise HTTPException(status_code=401)
    return {"user": user}
```

### Django - Middleware or Decorator
```python
# Option 1: Middleware (settings.py)
MIDDLEWARE = [
    # ...
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',
]
OIDC_PROTECTED_PATHS = ['/portal/', '/api/']
# All matching paths automatically protected

# Option 2: Decorator
from energydeskapi.auth.auth_django import create_auth_from_settings

auth = create_auth_from_settings()

@auth.require_auth_decorator
def protected_view(request):
    user_info = request.session.get('oidc_user')
    return HttpResponse(f"Hello {user_info['name']}")

# Option 3: Manual check
def manual_view(request):
    user = auth.get_current_user(request)
    if not user:
        return redirect(reverse('oidc_login'))
    return HttpResponse(f"Hello {user['name']}")
```

## Session Storage

### FastAPI
```python
# Uses Starlette SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
    session_cookie="clearing_session",
    max_age=3600 * 24  # 24 hours
)

# Session data stored in cookie (signed)
request.session['user'] = {
    'provider': 'azure',
    'email': 'user@example.com',
    'name': 'John Doe',
    'sub': 'unique-id',
    'authenticated': True
}
```

### Django
```python
# Uses Django's session framework (settings.py)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Database
# or 'django.contrib.sessions.backends.cached_db'  # Cache + DB
# or 'django.contrib.sessions.backends.cache'  # Cache only
# or 'django.contrib.sessions.backends.file'  # File system
# or 'django.contrib.sessions.backends.signed_cookies'  # Cookie

# Session data accessed the same way
request.session['oidc_user'] = {
    'provider': 'azure',
    'email': 'user@example.com',
    'name': 'John Doe',
    'sub': 'unique-id',
    'authenticated': True
}

# Requires migration: python manage.py migrate
```

## User Management

### FastAPI
```python
# No automatic user creation
# User info only in session
user = request.session.get('user')
# {
#     'provider': 'azure',
#     'email': 'user@example.com',
#     'name': 'John Doe',
#     'sub': 'unique-id',
#     'authenticated': True
# }

# You must manually integrate with your user system
```

### Django
```python
# Automatic Django User creation/update
email = user_info.get('email')
if email:
    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            'email': email,
            'first_name': user_info.get('given_name', '')[:30],
            'last_name': user_info.get('family_name', '')[:30],
        }
    )
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

# Access both OIDC data and Django user
oidc_user = request.session.get('oidc_user')
django_user = request.user  # Django User object
```

## Accessing User Information

### FastAPI
```python
# In route handler
@app.get("/me")
async def get_me(request: Request, user: dict = Depends(auth.require_auth)):
    return {
        "provider": user['provider'],
        "email": user['email'],
        "name": user['name'],
        "sub": user['sub']
    }

# Or manual
@app.get("/me2")
async def get_me2(request: Request):
    user = request.session.get('user')
    return {"user": user}
```

### Django
```python
# In view
def profile_view(request):
    # OIDC user info
    oidc_user = request.session.get('oidc_user')
    
    # Django user (automatically created)
    if request.user.is_authenticated:
        django_username = request.user.username
        django_email = request.user.email
    
    return JsonResponse({
        "oidc_provider": oidc_user['provider'],
        "oidc_email": oidc_user['email'],
        "django_username": request.user.username,
        "django_is_authenticated": request.user.is_authenticated
    })

# In template
# {{ request.session.oidc_user.name }}
# {{ request.user.username }}
```

## Middleware Configuration

### FastAPI
```python
# Middleware added by init_app()
def init_app(self, app: FastAPI, config: Optional[Dict[str, Any]] = None):
    app.add_middleware(
        SessionMiddleware,
        secret_key=self.secret_key,
        session_cookie="clearing_session",
        max_age=3600 * 24
    )
    # ...register routes...
```

### Django
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Required
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Required
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add OIDC middleware (optional, for automatic path protection)
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',
]

# Configure protected paths
OIDC_PROTECTED_PATHS = ['/portal/', '/api/']
OIDC_EXEMPT_PATHS = ['/admin/', '/auth/', '/static/']
```

## Configuration Structure

### FastAPI
```python
# Pass directly to constructor
config = {
    'azure': {
        'client_id': 'xxx',
        'client_secret': 'xxx',
        'tenant': 'common'
    },
    'google': {
        'client_id': 'xxx',
        'client_secret': 'xxx'
    },
    'django': {  # For Django OAuth Toolkit provider
        'client_id': 'xxx',
        'client_secret': 'xxx',
        'base_url': 'https://oauth-server.com',
        'authorization_endpoint': '/o/authorize/',
        'token_endpoint': '/o/token/',
        'userinfo_endpoint': '/oauth_edesk/userinfo/',
        'jwks_uri': '/o/.well-known/jwks.json'
    }
}

auth = FastAPIOIDCAuth(title="...", app=app, config=config)
```

### Django
```python
# settings.py
OIDC_TITLE = "My Application"

OIDC_PROVIDERS = {
    'azure': {
        'client_id': 'xxx',
        'client_secret': 'xxx',
        'tenant': 'common'
    },
    'google': {
        'client_id': 'xxx',
        'client_secret': 'xxx'
    },
    'django_oauth': {  # Note: different key name
        'client_id': 'xxx',
        'client_secret': 'xxx',
        'base_url': 'https://oauth-server.com',
        'authorization_endpoint': '/o/authorize/',
        'token_endpoint': '/o/token/',
        'userinfo_endpoint': '/oauth_edesk/userinfo/',
        'jwks_uri': '/o/.well-known/jwks.json'
    }
}

# Create from settings
auth = create_auth_from_settings()
```

## Logout

### FastAPI
```python
@app.get('/auth/logout')
async def logout(request: Request):
    request.session.clear()
    root_path = request.scope.get("root_path", "")
    return RedirectResponse(url=f'{root_path}/auth/login')
```

### Django
```python
def logout_view(self, request):
    request.session.pop('oidc_user', None)
    logout(request)  # Django's logout function
    script_name = request.META.get('SCRIPT_NAME', '')
    return redirect(f'{script_name}{reverse("oidc_login")}')
```

## Redirect URI Building

### FastAPI
```python
# Handle X-Forwarded-Proto and root_path
root_path = request.scope.get("root_path", "")
scheme = request.headers.get('X-Forwarded-Proto', request.url.scheme)
netloc = request.url.netloc
redirect_uri = f"{scheme}://{netloc}{root_path}/auth/authorize/{provider}"
```

### Django
```python
# Use build_absolute_uri
redirect_uri = request.build_absolute_uri(
    reverse('oidc_authorize', kwargs={'provider': provider})
)

# Django automatically handles:
# - X-Forwarded-Host (if USE_X_FORWARDED_HOST = True)
# - X-Forwarded-Proto (if SECURE_PROXY_SSL_HEADER set)
```

## Templates/UI

### FastAPI
```python
# HTML string in Python
html = f'''
<!DOCTYPE html>
<html>
<head><title>{self.title}</title></head>
<body>
    <h1>Login</h1>
    <!-- ... -->
</body>
</html>
'''
return HTMLResponse(html)
```

### Django
```python
# Can use same approach (HTML string)
html = f'''<!DOCTYPE html>...'''
return HttpResponse(html)

# Or use Django templates
return render(request, 'auth/login.html', {
    'title': self.title,
    'providers': available_providers
})
```

## Testing Locally

### FastAPI
```bash
# Run with uvicorn
uvicorn main:app --reload --port 8000

# Or with python
python main.py

# Visit http://localhost:8000/auth/login
```

### Django
```bash
# Run Django development server
python manage.py migrate  # First time only
python manage.py runserver

# Visit http://localhost:8000/auth/login/
```

## Production Deployment

### FastAPI
```bash
# With Gunicorn + Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# With Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Behind nginx for static files and SSL
```

### Django
```bash
# With Gunicorn
gunicorn myproject.wsgi:application --workers 4

# Or with uWSGI
uwsgi --http :8000 --module myproject.wsgi

# Behind nginx for static files and SSL
# Collect static files first:
python manage.py collectstatic
```

## Summary

| Feature | Best For |
|---------|----------|
| **FastAPI** | Microservices, APIs, async workloads, modern Python |
| **Django** | Full web applications, admin interface, ORM, traditional MVC |

Both implementations provide:
- ✅ Same OAuth providers (Azure, Google, Django OAuth)
- ✅ Same beautiful login UI
- ✅ Same security features (HTTPS, signed sessions, CSRF)
- ✅ Same user experience
- ✅ Production-ready code

Choose based on your framework:
- Using FastAPI? → Use `auth_fastapi.py`
- Using Django? → Use `auth_django.py`
- Using both? → Include both in your SDK!
