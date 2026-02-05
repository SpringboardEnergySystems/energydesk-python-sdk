# EnergyDesk SDK - Django OIDC Authentication

## 📦 What Was Created

A complete Django-compatible OIDC authentication module that mirrors the FastAPI version, allowing you to include this SDK in your Django portal project.

### New Files

1. **`auth_django.py`** (702 lines)
   - Main Django authentication module
   - `DjangoOIDCAuth` class - Multi-provider OIDC handler
   - `OIDCAuthMiddleware` - Automatic path protection
   - `create_auth_from_settings()` - Helper to load from Django settings

2. **`README_DJANGO.md`**
   - Complete documentation with all features
   - Installation and configuration instructions
   - Security best practices
   - Troubleshooting guide

3. **`QUICKSTART_DJANGO.md`**
   - Quick reference guide
   - Minimal setup instructions
   - Common use cases
   - Ready-to-copy code snippets

4. **`django_example.py`**
   - Comprehensive examples
   - Settings configuration
   - URL patterns
   - View protection methods
   - Template usage
   - API integration

5. **`COMPARISON.md`**
   - Side-by-side comparison of FastAPI vs Django versions
   - Feature parity matrix
   - Code examples for both frameworks
   - Migration guide

6. **Updated `__init__.py`**
   - Exports both Django and FastAPI modules
   - Graceful ImportError handling
   - Clean API surface

## ✨ Key Features

### Multi-Provider OIDC Authentication
- ✅ **Azure AD** - Microsoft enterprise authentication
- ✅ **Google** - Google workspace and consumer accounts
- ✅ **Django OAuth Toolkit** - Connect to other Django apps

### Django Integration
- ✅ **Automatic User Creation** - Creates/updates Django User objects
- ✅ **Session Management** - Uses Django's built-in session framework
- ✅ **Middleware Support** - Automatic protection for configured paths
- ✅ **Decorator Support** - Manual protection for specific views
- ✅ **Django Admin Compatible** - Works alongside Django's admin

### Security
- ✅ **HTTPS Support** - Production-ready SSL configuration
- ✅ **CSRF Protection** - Integrated with Django's CSRF middleware
- ✅ **Secure Sessions** - HttpOnly, Secure, SameSite cookies
- ✅ **Reverse Proxy Support** - Works behind nginx/Apache

### User Experience
- ✅ **Beautiful UI** - Same styled login page as FastAPI version
- ✅ **Provider Selection** - Modal overlay with multiple options
- ✅ **Automatic Redirects** - Returns to original page after login
- ✅ **Profile Page** - Example protected route

## 🚀 Quick Start

### 1. Install in Your Django Project

```bash
pip install energydeskapi authlib
```

### 2. Configure Django Settings

```python
# settings.py
OIDC_TITLE = "My Energy Portal"

OIDC_PROVIDERS = {
    'azure': {
        'client_id': os.environ.get('AZURE_CLIENT_ID'),
        'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
        'tenant': 'common'
    }
}

OIDC_PROTECTED_PATHS = ['/portal/']

MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',  # Add this
]
```

### 3. Add URL Patterns

```python
# urls.py
from energydeskapi.auth.auth_django import create_auth_from_settings

oidc_auth = create_auth_from_settings()

urlpatterns = [
    path('auth/', include(oidc_auth.get_urls())),
    # ... your URLs ...
]
```

### 4. Use in Views

```python
# Automatically protected by middleware
def portal_view(request):
    user_info = request.session.get('oidc_user')
    return HttpResponse(f"Welcome {user_info['name']}!")
```

## 📚 Documentation Guide

### Getting Started
1. **Start here**: `QUICKSTART_DJANGO.md` - Quick setup and common patterns
2. **Full docs**: `README_DJANGO.md` - Complete documentation
3. **Examples**: `django_example.py` - Copy-paste ready code

### Understanding the Code
4. **Comparison**: `COMPARISON.md` - FastAPI vs Django differences
5. **Source**: `auth_django.py` - Implementation details

## 🎯 Use Cases

### Use Case 1: Protect Entire Portal (Middleware)
```python
# settings.py
OIDC_PROTECTED_PATHS = ['/portal/']
OIDC_EXEMPT_PATHS = ['/admin/', '/auth/']

# All /portal/* URLs automatically require authentication
```

### Use Case 2: Protect Specific Views (Decorator)
```python
from energydeskapi.auth.auth_django import create_auth_from_settings

oidc_auth = create_auth_from_settings()

@oidc_auth.require_auth_decorator
def sensitive_view(request):
    return HttpResponse("Protected content")
```

### Use Case 3: Optional Authentication
```python
def public_view(request):
    user = request.session.get('oidc_user')
    if user:
        return HttpResponse(f"Welcome back, {user['name']}!")
    return HttpResponse("Welcome, guest!")
```

### Use Case 4: API Endpoints
```python
from rest_framework.decorators import api_view

@api_view(['GET'])
@oidc_auth.require_auth_decorator
def api_endpoint(request):
    user_info = request.session.get('oidc_user')
    return Response({
        'user': user_info,
        'data': get_user_data(user_info['email'])
    })
```

## 🔄 Integration Workflow

```
Your Django Portal Project
    ├── requirements.txt
    │   └── energydeskapi  # Add this
    │
    ├── settings.py
    │   ├── OIDC_TITLE = "..."
    │   ├── OIDC_PROVIDERS = {...}
    │   ├── OIDC_PROTECTED_PATHS = [...]
    │   └── MIDDLEWARE += ['energydeskapi.auth.auth_django.OIDCAuthMiddleware']
    │
    ├── urls.py
    │   └── path('auth/', include(oidc_auth.get_urls()))
    │
    └── views.py
        └── Use session['oidc_user'] or @decorator
```

## 🔐 OAuth Provider Setup

### Azure AD Setup
1. Go to Azure Portal → App registrations
2. Create new registration
3. Add redirect URI: `https://yourdomain.com/auth/authorize/azure/`
4. Create client secret
5. Copy Application (client) ID and Directory (tenant) ID
6. Add to Django settings

### Google Setup
1. Go to Google Cloud Console → Credentials
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URI: `https://yourdomain.com/auth/authorize/google/`
4. Copy Client ID and Client Secret
5. Add to Django settings

### Django OAuth Toolkit Setup
1. Install on OAuth server: `pip install django-oauth-toolkit`
2. Create application in admin
3. Set redirect URI: `https://yourdomain.com/auth/authorize/django_oauth/`
4. Copy Client ID and Secret
5. Configure endpoints in Django settings

## 🎨 User Interface

The login page features:
- 🎭 **Modal overlay** design
- 🎨 **EnergyDesk branding** (customizable)
- 🔒 **Provider buttons** (Azure, Google, Django OAuth)
- 📱 **Responsive** layout
- ♿ **Accessible** markup

## 🧪 Testing

### Local Development
```bash
# 1. Configure OAuth providers (use http://localhost:8000 for redirect URIs)
# 2. Set environment variables
export AZURE_CLIENT_ID="..."
export AZURE_CLIENT_SECRET="..."
export DJANGO_SECRET_KEY="..."

# 3. Run migrations
python manage.py migrate

# 4. Start server
python manage.py runserver

# 5. Visit http://localhost:8000/auth/login/
```

### Production Deployment
```bash
# 1. Configure OAuth providers (use https://yourdomain.com for redirect URIs)
# 2. Set environment variables in production
# 3. Configure nginx/Apache with SSL
# 4. Collect static files
python manage.py collectstatic

# 5. Run with Gunicorn
gunicorn myproject.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

## 📊 Comparison with FastAPI Version

| Feature | FastAPI | Django | Notes |
|---------|---------|--------|-------|
| **Framework** | FastAPI + Starlette | Django | Both work |
| **Session Storage** | Cookie (signed) | DB/Cache/Cookie | Django more flexible |
| **User Management** | Manual | Automatic | Django creates User objects |
| **Protection Method** | Dependency injection | Middleware/Decorator | Different patterns |
| **URL Registration** | Automatic | Manual include | Django more explicit |
| **Configuration** | Constructor params | Settings file | Django more structured |

**Both versions provide the same:**
- OAuth providers
- Security features
- Login UI/UX
- Production readiness

## 🛠️ Customization

### Custom Title
```python
# Option 1: In settings
OIDC_TITLE = "My Custom Portal"

# Option 2: When creating
auth = DjangoOIDCAuth(title="My Custom Portal", config=...)
```

### Custom Redirect After Login
```python
# Automatically stored and restored
def my_view(request):
    request.session['oidc_next'] = '/custom/path/'
    return redirect(reverse('oidc_login'))
```

### Custom User Logic
```python
class CustomOIDCAuth(DjangoOIDCAuth):
    def authorize_view(self, request, provider):
        response = super().authorize_view(request, provider)
        user_info = request.session.get('oidc_user')
        # Add custom logic here
        return response
```

## 🐛 Troubleshooting

### "Redirect URI mismatch"
- Ensure exact match in OAuth provider settings
- Check for trailing slashes
- Verify HTTP vs HTTPS

### "Session not persisting"
```python
# Ensure sessions are configured
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Run migrations
python manage.py migrate
```

### "Behind reverse proxy"
```python
# Add to settings.py
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## 📞 Support

### Documentation Files
- 📖 `README_DJANGO.md` - Full documentation
- ⚡ `QUICKSTART_DJANGO.md` - Quick start guide
- 📝 `django_example.py` - Code examples
- 🔄 `COMPARISON.md` - FastAPI vs Django

### Code
- 💻 `auth_django.py` - Implementation
- 🔗 `auth_fastapi.py` - FastAPI version (for reference)

## ✅ What You Can Do Now

1. ✅ **Install the SDK** in your Django portal project
2. ✅ **Configure OIDC providers** in Django settings
3. ✅ **Add URL patterns** to your urls.py
4. ✅ **Protect your views** with middleware or decorator
5. ✅ **Test locally** with development server
6. ✅ **Deploy to production** with proper security

## 🎉 Summary

You now have a **production-ready Django OIDC authentication module** that:
- Mirrors the FastAPI version's functionality
- Integrates seamlessly with Django
- Provides multiple protection methods
- Includes comprehensive documentation
- Supports multiple OAuth providers
- Creates Django users automatically
- Works behind reverse proxies
- Has a beautiful UI

**The module is ready to be included in your Django portal as part of the energydesk-python-sdk!**

---

**Need help?** Check the documentation files or examine the examples in `django_example.py`.

**Want to compare?** See `COMPARISON.md` for FastAPI vs Django differences.

**Ready to integrate?** Start with `QUICKSTART_DJANGO.md` for the fastest path.
