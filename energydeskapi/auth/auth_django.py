"""
Configurable OIDC Authentication Component for Django
Supports Azure AD, Google, and Django OAuth Toolkit
"""

# Import only non-model Django components at module level to avoid "apps aren't loaded yet" error
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import path, reverse
# Note: Don't import settings here if we want to use this in settings.py
# from django.conf import settings
from authlib.integrations.django_client import OAuth
from functools import wraps
import os
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Lazy imports for Django components that require apps to be loaded
def _get_django_auth():
    """Lazy import of django.contrib.auth to avoid apps loading issues"""
    from django.contrib.auth import login, logout
    return login, logout

def _get_user_model():
    """Lazy import of User model to avoid apps loading issues"""
    from django.contrib.auth.models import User
    return User

def _get_reverse():
    """Lazy import of reverse to avoid apps loading issues"""
    from django.urls import reverse
    return reverse


class DjangoOIDCAuth:
    """Multi-provider OIDC authentication handler for Django"""

    PROVIDER_CONFIGS = {
        'azure': {
            'name': 'azure',
            'server_metadata_url': 'https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration',
            'client_kwargs': {'scope': 'openid email profile'},
            'display_name': 'Microsoft Azure AD'
        },
        'google': {
            'name': 'google',
            'server_metadata_url': 'https://accounts.google.com/.well-known/openid-configuration',
            'client_kwargs': {'scope': 'openid email profile'},
            'display_name': 'Google'
        },
        'django_oauth': {
            'name': 'django_oauth',
            'server_metadata_url': None,  # Will be set from config
            'client_kwargs': {'scope': 'email profile'},
            'display_name': 'Django OAuth'
        }
    }

    def __init__(self, title: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OIDC Auth for Django

        Config structure:
        {
            'azure': {
                'client_id': 'your-client-id',
                'client_secret': 'your-client-secret',
                'tenant': 'your-tenant-id-or-common'
            },
            'google': {
                'client_id': 'your-client-id.apps.googleusercontent.com',
                'client_secret': 'your-client-secret'
            },
            'django_oauth': {
                'client_id': 'your-client-id',
                'client_secret': 'your-client-secret',
                'base_url': 'https://your-django-app.com',
                'authorization_endpoint': '/o/authorize/',
                'token_endpoint': '/o/token/',
                'userinfo_endpoint': '/o/userinfo/',
                'jwks_uri': '/o/.well-known/jwks.json'
            }
        }
        """
        self.oauth = OAuth()
        self.providers = {}
        self.title = title
        self.config = config or {}

        if config:
            self._register_providers(config)

    def _register_providers(self, config: Dict[str, Any]):
        """Register OAuth providers based on config"""
        for provider_key, provider_config in config.items():
            if provider_key not in self.PROVIDER_CONFIGS:
                logger.warning(f"Unknown provider: {provider_key}")
                continue

            template = self.PROVIDER_CONFIGS[provider_key].copy()

            # Handle Azure tenant replacement
            if provider_key == 'azure' and 'tenant' in provider_config:
                template['server_metadata_url'] = template['server_metadata_url'].format(
                    tenant=provider_config['tenant']
                )

            # Handle Django custom endpoints
            if provider_key == 'django_oauth' and 'base_url' in provider_config:
                base_url = provider_config['base_url'].rstrip('/')
                template['authorize_url'] = base_url + provider_config.get('authorization_endpoint', '/o/authorize/')
                template['access_token_url'] = base_url + provider_config.get('token_endpoint', '/o/token/')
                template['userinfo_endpoint'] = base_url + provider_config.get('userinfo_endpoint', '/oauth_edesk/userinfo/')
                template['jwks_uri'] = base_url + provider_config.get('jwks_uri', '/o/.well-known/jwks.json')
                template['server_metadata_url'] = None

            # Register with Authlib for Django
            oauth_config = {
                'client_id': provider_config['client_id'],
                'client_secret': provider_config['client_secret'],
                'client_kwargs': template['client_kwargs']
            }

            if template.get('server_metadata_url'):
                oauth_config['server_metadata_url'] = template['server_metadata_url']
            else:
                # For Django or custom providers
                if template.get('authorize_url'):
                    oauth_config['authorize_url'] = template['authorize_url']
                if template.get('access_token_url'):
                    oauth_config['access_token_url'] = template['access_token_url']
                if template.get('userinfo_endpoint'):
                    oauth_config['userinfo_endpoint'] = template['userinfo_endpoint']
                if template.get('jwks_uri'):
                    oauth_config['jwks_uri'] = template['jwks_uri']

            self.providers[provider_key] = self.oauth.register(
                name=provider_key,
                **oauth_config
            )
            logger.info(f"Registered OIDC provider: {provider_key}")

    def get_urls(self):
        """Return URL patterns for Django"""
        return [
            path('login/', self.login_view, name='oidc_login'),
            path('login/<str:provider>/', self.login_provider_view, name='oidc_login_provider'),
            path('authorize/<str:provider>/', self.authorize_view, name='oidc_authorize'),
            path('logout/', self.logout_view, name='oidc_logout'),
            path('profile/', self.profile_view, name='oidc_profile'),
        ]

    def login_view(self, request):
        """Show provider selection page as a modal overlay"""
        # Build URL prefix if needed
        reverse_func = _get_reverse()
        script_name = request.META.get('SCRIPT_NAME', '')

        available_providers = [
            {
                'key': key,
                'name': self.PROVIDER_CONFIGS[key]['display_name'],
                'login_url': f'{script_name}{reverse_func("oidc_login_provider", kwargs={"provider": key})}'
            }
            for key in self.providers.keys()
        ]

        # Modal overlay login page on top of dashboard
        html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Login - {self.title}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
            <link rel="icon" href="{script_name}/static/energydesk/images/energydesk_icon.png">
            
            <!-- CSS from base.html -->
            <link rel="stylesheet" href="{script_name}/static/energydesk/app/css/bootstrap.css">
            <link rel="stylesheet" href="{script_name}/static/energydesk/brightcss/style.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            
            <style>
                body {{
                    background: #f5f5f5;
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    overflow: hidden;
                }}
                
                .body-inner {{
                    background: #f5f5f5;
                    min-height: 100vh;
                    position: relative;
                }}
                
                /* Background dashboard - blurred and grayed out */
                .dashboard-background {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 1;
                    filter: blur(5px);
                    opacity: 0.3;
                    pointer-events: none;
                }}
                
                .text-green {{
                    color: #53B092;
                }}
                
                .logotext {{
                    -webkit-text-stroke-width: 0.1px;
                    -webkit-text-stroke-color: grey;
                    text-transform: uppercase;
                    margin-left: 60px;
                    font-size: 18px;
                }}
                
                #header {{
                    background: white;
                    padding: 20px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                
                /* Green navigation bar */
                #nav-wrapper {{
                    background: #53B092;
                    margin-bottom: 30px;
                }}
                
                #nav-wrapper .navbar {{
                    background: #53B092;
                    border: none;
                    margin-bottom: 0;
                    min-height: 50px;
                }}
                
                #nav-wrapper .navbar-nav > li > a {{
                    color: white;
                    padding: 15px 20px;
                    font-weight: 500;
                }}
                
                #nav-wrapper .navbar-nav > li > a:hover,
                #nav-wrapper .navbar-nav > li > a:focus {{
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                }}
                
                #nav-wrapper .navbar-nav > .disabled > a {{
                    color: rgba(255, 255, 255, 0.5);
                    cursor: not-allowed;
                }}
                
                /* Modal overlay */
                .login-overlay {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.6);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    backdrop-filter: blur(3px);
                }}
                
                .login-modal {{
                    background: white;
                    padding: 50px 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    border-top: 6px solid #53B092;
                    max-width: 480px;
                    width: 90%;
                    animation: slideIn 0.3s ease-out;
                    position: relative;
                }}
                
                @keyframes slideIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(-30px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                
                .login-modal h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 10px;
                    font-size: 32px;
                    font-weight: 600;
                }}
                
                .login-modal p {{
                    text-align: center;
                    color: #666;
                    margin-bottom: 35px;
                    font-size: 15px;
                }}
                
                .provider-btn {{
                    display: block;
                    padding: 18px 24px;
                    margin: 15px 0;
                    text-decoration: none;
                    background: #53B092;
                    color: white;
                    border-radius: 8px;
                    text-align: center;
                    transition: all 0.3s ease;
                    font-weight: 500;
                    font-size: 16px;
                    border: none;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                }}
                
                .provider-btn:hover {{
                    background: #469d82;
                    transform: translateY(-3px);
                    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                    color: white;
                    text-decoration: none;
                }}
                
                .provider-btn i {{
                    margin-right: 12px;
                    font-size: 20px;
                }}
                
                .azure {{ 
                    background: #0078d4; 
                }}
                .azure:hover {{ 
                    background: #005a9e; 
                }}
                
                .google {{ 
                    background: #db4437; 
                }}
                .google:hover {{ 
                    background: #c23321; 
                }}
                
                .django_oauth {{ 
                    background: #0c4b33; 
                }}
                .django_oauth:hover {{ 
                    background: #092f21; 
                }}
                
                .footer-text {{
                    text-align: center;
                    color: #999;
                    margin-top: 30px;
                    font-size: 13px;
                }}
                
                .lock-icon {{
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 48px;
                    color: #53B092;
                    font-weight: 600;
                }}
                
                .lock-icon i {{
                    font-size: 48px;
                    color: #53B092;
                }}
            </style>
        </head>
        <body>
            <div class="body-inner">
                <!-- Blurred Dashboard Background -->
                <div class="dashboard-background">
                    <!-- Header -->
                    <header id="header" class="header">
                        <div class="container">
                            <div class="row">
                                <div class="col-sm-12">
                                    <div class="row">
                                        <div class="logo col-xs-12 col-sm-12" style="text-align: center;">
                                            <a href="{script_name}/">
                                                <img src="{script_name}/static/energydesk/brightimages/edesk2.png" alt="EnergyDesk" style="max-height: 60px;">
                                            </a>
                                            <br/>
                                            <div class="logotext text-green" style="margin-left: 0;">{self.title}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </header>
                    
                    <!-- Green Navigation Bar -->
                    <div id="nav-wrapper">
                        <nav class="navbar navbar-default" role="navigation">
                            <div class="container">
                                <div class="navbar-header">
                                    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar-collapse">
                                        <span class="sr-only">Toggle navigation</span>
                                        <span class="icon-bar"></span>
                                        <span class="icon-bar"></span>
                                        <span class="icon-bar"></span>
                                    </button>
                                </div>
                                <div class="collapse navbar-collapse" id="navbar-collapse">
                                    <ul class="nav navbar-nav">
                                        <li class="disabled"><a href="#" style="cursor: not-allowed;"><i class="fa fa-tachometer"></i> Dashboard</a></li>
                                        <li class="disabled"><a href="#" style="cursor: not-allowed;"><i class="fa fa-exchange"></i> Trades</a></li>
                                        <li class="disabled"><a href="#" style="cursor: not-allowed;"><i class="fa fa-balance-scale"></i> Reconciliation</a></li>
                                        <li class="disabled"><a href="#" style="cursor: not-allowed;"><i class="fa fa-book"></i> Ledger</a></li>
                                        <li><a href="{script_name}/docs" target="_blank"><i class="fa fa-code"></i> API</a></li>
                                    </ul>
                                </div>
                            </div>
                        </nav>
                    </div>
                    
                    <!-- Placeholder content -->
                    <div class="container">
                        <div style="height: 400px; display: flex; align-items: center; justify-content: center; color: #999;">
                            <div style="text-align: center;">
                                <i class="fa fa-lock" style="font-size: 80px; opacity: 0.3;"></i>
                                <h2 style="opacity: 0.3;">Dashboard</h2>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Login Modal Overlay -->
                <div class="login-overlay">
                    <div class="login-modal">
                        <div class="lock-icon">
                           EnergyDesk <i class="fa fa-lock"></i>
                           <div style="font-size: 18px; margin-top: 10px; font-weight: 400;">{self.title}</div>
                        </div>
                        <h1>Authentication Required</h1>
                        <p>Please sign in with your credentials</p>
        '''

        # Add provider buttons with icons
        provider_icons = {
            'azure': 'fa-windows',
            'google': 'fa-google',
            'django_oauth': 'fa-lock'
        }

        for provider in available_providers:
            provider_class = provider['key']
            icon = provider_icons.get(provider_class, 'fa-sign-in')
            html += f'''
                        <a href="{provider["login_url"]}" class="provider-btn {provider_class}">
                            <i class="fa {icon}"></i> {provider["name"]}
                        </a>
            '''

        html += f'''
                        <div class="footer-text">
                            <i class="fa fa-shield"></i> Secure authentication powered by OIDC
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Bootstrap JS for mobile menu -->
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="{script_name}/static/energydesk/app/js/bootstrap.min.js"></script>
        </body>
        </html>
        '''
        return HttpResponse(html)

    def login_provider_view(self, request, provider):
        """Initiate OAuth flow for selected provider"""
        if provider not in self.providers:
            return HttpResponse('Invalid provider', status=400)

        reverse_func = _get_reverse()
        # Build redirect URI
        redirect_uri = request.build_absolute_uri(
            reverse_func('oidc_authorize', kwargs={'provider': provider})
        )

        logger.info(f"OAuth redirect URI: {redirect_uri}")

        return self.providers[provider].authorize_redirect(request, redirect_uri)

    def authorize_view(self, request, provider):
        """Handle OAuth callback"""
        if provider not in self.providers:
            return HttpResponse('Invalid provider', status=400)

        try:
            token = self.providers[provider].authorize_access_token(request)
        except Exception as e:
            logger.error(f"Error authorizing with {provider}: {e}", exc_info=True)
            return HttpResponse(f'Authorization failed: {str(e)}', status=401)

        # Get user info
        try:
            if provider == 'google':
                user_info = token.get('userinfo')
                if not user_info:
                    user_info = self.providers[provider].userinfo(token=token)
            else:
                user_info = self.providers[provider].userinfo(token=token)
        except Exception as e:
            logger.error(f"Error getting user info from {provider}: {e}", exc_info=True)
            return HttpResponse(f'Failed to get user info: {str(e)}', status=401)

        # Extract email
        email = user_info.get('email')

        # Store user info in session
        request.session['oidc_user'] = {
            'provider': provider,
            'email': email,
            'name': user_info.get('name', user_info.get('given_name', '')),
            'sub': user_info.get('sub'),
            'authenticated': True
        }

        # Store access token for backend API forwarding
        access_token = token.get('access_token')
        if access_token:
            # Store in both formats for compatibility
            request.session['api_token'] = access_token
            request.session['oidc_access_token'] = access_token
            request.session['token_type'] = 'Bearer'
            logger.info(f"Stored access token in session for API forwarding")

        # Store username and email for portal compatibility
        if email:
            request.session['username'] = email
            request.session['email'] = email
            logger.info(f"Stored username/email in session: {email}")

            # Create/update Django user
            User = _get_user_model()
            login_func, _ = _get_django_auth()
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': user_info.get('given_name', '')[:30],
                    'last_name': user_info.get('family_name', '')[:30],
                }
            )
            # Log the user into Django's session
            login_func(request, user, backend='django.contrib.auth.backends.ModelBackend')
            logger.info(f"User {email} authenticated via {provider} (created={created})")


        # Redirect to the original page or dashboard
        script_name = request.META.get('SCRIPT_NAME', '')
        next_url = request.session.get('oidc_next', f'{script_name}/')
        request.session.pop('oidc_next', None)
        return redirect(next_url)

    def logout_view(self, request):
        """Clear session and log out"""
        _, logout_func = _get_django_auth()
        reverse_func = _get_reverse()
        request.session.pop('oidc_user', None)
        request.session.pop('api_token', None)
        request.session.pop('oidc_access_token', None)
        request.session.pop('token_type', None)
        request.session.pop('username', None)
        request.session.pop('email', None)
        request.session.pop('usrprofile', None)
        logout_func(request)
        script_name = request.META.get('SCRIPT_NAME', '')
        return redirect(f'{script_name}{reverse_func("oidc_login")}')

    def profile_view(self, request):
        """Display user profile (protected route example)"""
        reverse_func = _get_reverse()
        user_info = request.session.get('oidc_user')
        script_name = request.META.get('SCRIPT_NAME', '')

        if not user_info:
            # Store the next URL before redirecting to login
            request.session['oidc_next'] = request.get_full_path()
            return redirect(f'{script_name}{reverse_func("oidc_login")}')

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Profile - {self.title}</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    max-width: 600px; 
                    margin: 50px auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #333; }}
                .info {{ margin: 15px 0; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ color: #333; margin-left: 10px; }}
                .logout-btn {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: #dc3545;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .logout-btn:hover {{ background: #c82333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>User Profile</h1>
                <div class="info">
                    <span class="label">Provider:</span>
                    <span class="value">{user_info.get('provider', 'N/A')}</span>
                </div>
                <div class="info">
                    <span class="label">Name:</span>
                    <span class="value">{user_info.get('name', 'N/A')}</span>
                </div>
                <div class="info">
                    <span class="label">Email:</span>
                    <span class="value">{user_info.get('email', 'N/A')}</span>
                </div>
                <div class="info">
                    <span class="label">Subject ID:</span>
                    <span class="value">{user_info.get('sub', 'N/A')}</span>
                </div>
                <div class="info">
                    <span class="label">Django User:</span>
                    <span class="value">{request.user.username if request.user.is_authenticated else 'Anonymous'}</span>
                </div>
                <a href="{script_name}{reverse_func('oidc_logout')}" class="logout-btn">Logout</a>
            </div>
        </body>
        </html>
        '''
        return HttpResponse(html)

    def get_current_user(self, request) -> Optional[Dict[str, Any]]:
        """Get current authenticated user from session"""
        user = request.session.get('oidc_user')
        if not user or not user.get('authenticated'):
            return None
        return user

    def require_auth_decorator(self, view_func):
        """Decorator to require authentication"""
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = self.get_current_user(request)
            if not user:
                reverse_func = _get_reverse()
                # Store the next URL
                request.session['oidc_next'] = request.get_full_path()
                script_name = request.META.get('SCRIPT_NAME', '')
                return redirect(f'{script_name}{reverse_func("oidc_login")}')
            return view_func(request, *args, **kwargs)
        return wrapper


class OIDCAuthMiddleware:
    """
    Django middleware to check OIDC authentication on protected paths

    Add to settings.py MIDDLEWARE:
        'energydeskapi.auth.auth_django.OIDCAuthMiddleware',

    Configure protected paths in settings.py:
        OIDC_PROTECTED_PATHS = ['/portal/', '/api/']
        OIDC_EXEMPT_PATHS = ['/admin/', '/auth/']
    """

    def __init__(self, get_response):
        from django.conf import settings
        self.get_response = get_response
        self.protected_paths = getattr(settings, 'OIDC_PROTECTED_PATHS', [])
        self.exempt_paths = getattr(settings, 'OIDC_EXEMPT_PATHS', ['/admin/', '/auth/', '/static/', '/media/'])

    def __call__(self, request):
        # Check if path should be protected
        path = request.path_info
        script_name = request.META.get('SCRIPT_NAME', '')

        # Check if path is exempt
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return self.get_response(request)

        # Check if path should be protected
        if any(path.startswith(protected) for protected in self.protected_paths):
            user = request.session.get('oidc_user')
            if not user or not user.get('authenticated'):
                reverse_func = _get_reverse()
                # Store the next URL
                request.session['oidc_next'] = request.get_full_path()
                return redirect(f'{script_name}{reverse_func("oidc_login")}')

        return self.get_response(request)


# Helper function to create auth instance from Django settings or environment variables
def create_auth_from_settings(title: str = None) -> DjangoOIDCAuth:
    """
    Create DjangoOIDCAuth instance from environment variables

    This function reads configuration directly from environment variables
    to avoid issues with Django apps not being loaded yet when settings are imported.

    Environment variables:
        OIDC_TITLE (optional): Application title
        AZURE_CLIENT_ID: Azure AD client ID
        AZURE_CLIENT_SECRET: Azure AD client secret
        AZURE_TENANT_ID: Azure AD tenant ID (defaults to 'common')
        GOOGLE_CLIENT_ID: Google OAuth client ID
        GOOGLE_CLIENT_SECRET: Google OAuth client secret
        DJANGO_OAUTH_CLIENT_ID: Django OAuth Toolkit client ID
        DJANGO_OAUTH_CLIENT_SECRET: Django OAuth Toolkit client secret
        DJANGO_OAUTH_BASE_URL: Django OAuth base URL
    """
    if title is None:
        title = os.environ.get('OIDC_TITLE', 'Django Application')

    # Build config from environment variables
    config = {}

    # Azure AD configuration
    azure_client_id = os.environ.get('AZURE_CLIENT_ID')
    azure_client_secret = os.environ.get('AZURE_CLIENT_SECRET')
    if azure_client_id and azure_client_secret:
        config['azure'] = {
            'client_id': azure_client_id,
            'client_secret': azure_client_secret,
            'tenant': os.environ.get('AZURE_TENANT_ID', 'common')
        }

    # Google configuration
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    if google_client_id and google_client_secret:
        config['google'] = {
            'client_id': google_client_id,
            'client_secret': google_client_secret
        }

    # Django OAuth Toolkit configuration
    django_client_id = os.environ.get('DJANGO_OAUTH_CLIENT_ID')
    django_client_secret = os.environ.get('DJANGO_OAUTH_CLIENT_SECRET')
    django_base_url = os.environ.get('DJANGO_OAUTH_BASE_URL')
    if django_client_id and django_client_secret and django_base_url:
        config['django_oauth'] = {
            'client_id': django_client_id,
            'client_secret': django_client_secret,
            'base_url': django_base_url,
            'authorization_endpoint': os.environ.get('DJANGO_OAUTH_AUTHORIZATION_ENDPOINT', '/o/authorize/'),
            'token_endpoint': os.environ.get('DJANGO_OAUTH_TOKEN_ENDPOINT', '/o/token/'),
            'userinfo_endpoint': os.environ.get('DJANGO_OAUTH_USERINFO_ENDPOINT', '/oauth_edesk/userinfo/'),
            'jwks_uri': os.environ.get('DJANGO_OAUTH_JWKS_URI', '/o/.well-known/jwks.json')
        }

    return DjangoOIDCAuth(title=title, config=config)
