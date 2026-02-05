"""
Example Django integration for OIDC authentication

This file shows how to integrate the DjangoOIDCAuth into your Django project.
"""

# ============================================================================
# Step 1: Add to your Django settings.py
# ============================================================================

"""
# settings.py

import os

# OIDC Authentication Configuration
OIDC_TITLE = "My Energy Portal"

OIDC_PROVIDERS = {
    'azure': {
        'client_id': os.environ.get('AZURE_CLIENT_ID'),
        'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
        'tenant': os.environ.get('AZURE_TENANT_ID', 'common')
    },
    'google': {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET')
    }
}

# Paths requiring authentication
OIDC_PROTECTED_PATHS = ['/portal/', '/api/']
OIDC_EXEMPT_PATHS = ['/admin/', '/auth/', '/static/', '/media/', '/docs/']

# Add middleware (after AuthenticationMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add OIDC middleware
    'energydeskapi.auth.auth_django.OIDCAuthMiddleware',
]

# Session configuration (required)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True  # Set to False in development
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# If behind reverse proxy (nginx, etc.)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
"""

# ============================================================================
# Step 2: Add to your main urls.py
# ============================================================================

"""
# urls.py

from django.contrib import admin
from django.urls import path, include
from energydeskapi.auth.auth_django import create_auth_from_settings

# Create OIDC auth instance from settings
oidc_auth = create_auth_from_settings()

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include OIDC authentication URLs
    # This adds: /auth/login/, /auth/login/<provider>/, 
    #            /auth/authorize/<provider>/, /auth/logout/, /auth/profile/
    path('auth/', include(oidc_auth.get_urls())),
    
    # Your application URLs
    path('portal/', include('myapp.urls')),
    path('api/', include('api.urls')),
    path('', include('home.urls')),
]
"""

# ============================================================================
# Step 3: Use in your views (Method 1: Middleware - Automatic)
# ============================================================================

"""
# views.py

from django.http import HttpResponse, JsonResponse

# If the path is in OIDC_PROTECTED_PATHS, middleware automatically protects it
def portal_dashboard(request):
    # This view is automatically protected by middleware
    user_info = request.session.get('oidc_user')
    
    return HttpResponse(f'''
        <h1>Welcome to the Portal</h1>
        <p>Name: {user_info['name']}</p>
        <p>Email: {user_info['email']}</p>
        <p>Provider: {user_info['provider']}</p>
        <a href="/auth/logout">Logout</a>
    ''')
"""

# ============================================================================
# Step 3: Use in your views (Method 2: Decorator - Manual)
# ============================================================================

"""
# views.py

from django.http import HttpResponse
from energydeskapi.auth.auth_django import create_auth_from_settings

# Create auth instance
oidc_auth = create_auth_from_settings()

# Protect specific views with decorator
@oidc_auth.require_auth_decorator
def protected_view(request):
    user_info = request.session.get('oidc_user')
    return HttpResponse(f"Hello {user_info['name']}!")

# Or check manually
def manual_check_view(request):
    user_info = oidc_auth.get_current_user(request)
    if not user_info:
        return HttpResponse("Please login", status=401)
    
    return HttpResponse(f"Hello {user_info['name']}!")
"""

# ============================================================================
# Step 4: Use in Django templates
# ============================================================================

"""
<!-- base.html -->

<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Portal{% endblock %}</title>
</head>
<body>
    <header>
        <h1>My Portal</h1>
        <nav>
            {% if request.user.is_authenticated %}
                <span>Welcome, {{ request.session.oidc_user.name }}!</span>
                <a href="{% url 'oidc_profile' %}">Profile</a>
                <a href="{% url 'oidc_logout' %}">Logout</a>
            {% else %}
                <a href="{% url 'oidc_login' %}">Login</a>
            {% endif %}
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
"""

# ============================================================================
# Step 5: Access user info in views
# ============================================================================

"""
# views.py

def my_view(request):
    # Method 1: From OIDC session
    oidc_user = request.session.get('oidc_user')
    if oidc_user:
        email = oidc_user['email']
        name = oidc_user['name']
        provider = oidc_user['provider']
        sub = oidc_user['sub']
    
    # Method 2: From Django user (automatically created)
    if request.user.is_authenticated:
        django_username = request.user.username  # Will be the email
        django_email = request.user.email
        first_name = request.user.first_name
        last_name = request.user.last_name
    
    # Both methods work together - OIDC creates/updates Django user
"""

# ============================================================================
# Step 6: API views with authentication
# ============================================================================

"""
# api/views.py

from django.http import JsonResponse
from energydeskapi.auth.auth_django import create_auth_from_settings

oidc_auth = create_auth_from_settings()

@oidc_auth.require_auth_decorator
def api_endpoint(request):
    user_info = request.session.get('oidc_user')
    
    return JsonResponse({
        'status': 'success',
        'user': {
            'email': user_info['email'],
            'name': user_info['name'],
            'provider': user_info['provider']
        },
        'data': {
            # Your API data
        }
    })

# Or use Django REST Framework
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
@oidc_auth.require_auth_decorator
def api_endpoint_drf(request):
    user_info = request.session.get('oidc_user')
    
    return Response({
        'user': user_info,
        'data': {}
    })
"""

# ============================================================================
# Step 7: Environment variables (.env file)
# ============================================================================

"""
# .env (DO NOT commit this file!)

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# Azure AD
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-tenant-id-or-common

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
"""

# ============================================================================
# Step 8: Load environment variables in settings.py
# ============================================================================

"""
# settings.py

import os
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Or use python-decouple
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

OIDC_PROVIDERS = {
    'azure': {
        'client_id': config('AZURE_CLIENT_ID'),
        'client_secret': config('AZURE_CLIENT_SECRET'),
        'tenant': config('AZURE_TENANT_ID', default='common')
    },
    'google': {
        'client_id': config('GOOGLE_CLIENT_ID'),
        'client_secret': config('GOOGLE_CLIENT_SECRET')
    }
}
"""

# ============================================================================
# Step 9: Run migrations and start server
# ============================================================================

"""
# Terminal commands

# Install dependencies
pip install energydeskapi authlib python-dotenv

# Run migrations (for session storage)
python manage.py migrate

# Create superuser (optional, for Django admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Visit http://localhost:8000/auth/login to test
"""

# ============================================================================
# Step 10: Production deployment (with nginx)
# ============================================================================

"""
# nginx.conf

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/your_cert.pem;
    ssl_certificate_key /etc/ssl/private/your_key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }
    
    location /static/ {
        alias /path/to/your/static/files/;
    }
}

# Configure OAuth redirect URIs:
# Azure: https://yourdomain.com/auth/authorize/azure/
# Google: https://yourdomain.com/auth/authorize/google/
"""

# ============================================================================
# Additional: Custom authentication logic
# ============================================================================

"""
# custom_views.py

from energydeskapi.auth.auth_django import DjangoOIDCAuth
from django.conf import settings

# Create custom auth instance with additional logic
class CustomOIDCAuth(DjangoOIDCAuth):
    
    def authorize_view(self, request, provider):
        # Call parent method
        response = super().authorize_view(request, provider)
        
        # Add custom logic after authentication
        user_info = request.session.get('oidc_user')
        if user_info:
            # Log to custom system
            log_user_login(user_info['email'], provider)
            
            # Check if user is allowed
            if not is_user_allowed(user_info['email']):
                request.session.clear()
                return HttpResponse('Access denied', status=403)
        
        return response

# Use custom class in urls.py
custom_auth = CustomOIDCAuth(
    title="My Portal",
    config=settings.OIDC_PROVIDERS
)
"""

if __name__ == '__main__':
    print("This is an example file. Copy the relevant code to your Django project.")
    print("See README_DJANGO.md for complete documentation.")
