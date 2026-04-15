"""
Configurable OIDC Authentication Component for FastAPI
Supports Azure AD, Google, and Django OAuth Toolkit
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from functools import wraps
import os
import threading
from typing import Optional, Dict, Any, Callable
import logging
from energydeskapi.auth.etrm_authorize import authorize_user_etrm
logger = logging.getLogger(__name__)

# Server-side token store: sub → access_token
# Keeps large Azure/Google JWTs out of the session cookie while still making
# them available for backend API calls (authorize_user_etrm, trade approval, etc.)
_token_store: Dict[str, str] = {}
_token_store_lock = threading.Lock()


class FastAPIOIDCAuth:
    """Multi-provider OIDC authentication handler for FastAPI"""

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
        'django': {
            'name': 'django',
            'server_metadata_url': None,  # Will be set from config
            'client_kwargs': {'scope': 'email profile'},
            'display_name': 'Django OAuth'
        }
    }

    def __init__(self,title:str,app: Optional[FastAPI] = None, config: Optional[Dict[str, Any]] = None, secret_key: Optional[str] = None, allow_guest: bool = False):
        """
        Initialize OIDC Auth for FastAPI

        Args:
            title: Application title for the login page
            app: FastAPI application instance
            config: OIDC provider configuration dictionary
            secret_key: Secret key for session middleware
            allow_guest: Allow unauthenticated guest access (default: False)

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
            'django': {
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
        self.secret_key = secret_key or os.urandom(24).hex()
        self.app = app
        self.title = title
        self.allow_guest = allow_guest
        # Optional post-auth hook — see set_post_auth_hook() for details.
        self.post_auth_hook = None

        if app:
            self.init_app(app, config)

    def init_app(self,  app: FastAPI, config: Optional[Dict[str, Any]] = None):
        """Initialize with FastAPI app"""

        # Add session middleware.
        # NOTE: Do NOT use same_site="none" without https_only=True — browsers reject
        # SameSite=None cookies that lack the Secure flag.
        # SameSite=lax is correct here: Azure/Google redirect back to the SAME domain
        # (e.g. hafslund.energydesk.no → hafslund.energydesk.no/clearing/auth/authorize/azure)
        # which is a same-site top-level navigation, so lax allows the cookie to be sent.
        app.add_middleware(
            SessionMiddleware,
            secret_key=self.secret_key,
            session_cookie="clearing_session",
            max_age=3600 * 24,  # 24 hours
        )

        # Store app reference for OAuth
        self.app = app

        if config:
            self.config = config  # Store config for later use
            self._register_providers(config)

        # Register routes
        self._register_routes(app=self.app, allow_guest=self.allow_guest)

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
            if provider_key == 'django' and 'base_url' in provider_config:
                base_url = provider_config['base_url'].rstrip('/')
                template['authorize_url'] = base_url + provider_config.get('authorization_endpoint', '/o/authorize/')
                template['access_token_url'] = base_url + provider_config.get('token_endpoint', '/o/token/')
                template['userinfo_endpoint'] = base_url + provider_config.get('userinfo_endpoint', '/oauth_edesk/userinfo/')
                template['jwks_uri'] = base_url + provider_config.get('jwks_uri', '/o/.well-known/jwks.json')
                template['server_metadata_url'] = None

                logger.info(f"[DJANGO] Constructed URLs:")
                logger.info(f"  - authorize_url: {template['authorize_url']}")
                logger.info(f"  - access_token_url: {template['access_token_url']}")
                logger.info(f"  - userinfo_endpoint: {template['userinfo_endpoint']}")
                logger.info(f"  - jwks_uri: {template['jwks_uri']}")

            # Register with Authlib for Starlette
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

    def _register_routes(self, app: FastAPI, allow_guest: bool = False):
        """Register authentication routes"""

        @app.get('/auth/login', response_class=HTMLResponse)
        async def login(request: Request):
            """Show provider selection page as a modal overlay"""
            # Get root_path for generating URLs with prefix
            root_path = request.scope.get("root_path", "")

            available_providers = [
                {
                    'key': key,
                    'name': self.PROVIDER_CONFIGS[key]['display_name'],
                    'login_url': f'{root_path}/auth/login/{key}'
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
                <link rel="icon" href="{root_path}/static/energydesk/images/energydesk_icon.png">
                
                <!-- CSS from base.html -->
                <link rel="stylesheet" href="{root_path}/static/energydesk/app/css/bootstrap.css">
                <link rel="stylesheet" href="{root_path}/static/energydesk/brightcss/style.css">
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
                    
                    .django {{ 
                        background: #0c4b33; 
                    }}
                    .django:hover {{ 
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
                
                    .lock-icon {{
                        text-align: center;
                        margin-bottom: 20px;
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
                                                <a href="{root_path}/">
                                                    <img src="{root_path}/static/energydesk/brightimages/edesk2.png" alt="EnergyDesk" style="max-height: 60px;">
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
                                            <li><a href="{root_path}/docs" target="_blank"><i class="fa fa-code"></i> API</a></li>
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
                            <h2>Authentication Required</h2>
                            <p>Please sign in via one of these services</p>
            '''

            # Add provider buttons with icons
            provider_icons = {
                'azure': 'fa-windows',
                'google': 'fa-google',
                'django': 'fa-lock'
            }

            for provider in available_providers:
                provider_class = provider['key']
                icon = provider_icons.get(provider_class, 'fa-sign-in')
                html += f'''
                            <a href="{provider["login_url"]}" class="provider-btn {provider_class}">
                                <i class="fa {icon}"></i> {provider["name"]}
                            </a>
                '''
            logger.info(f"Login with guest allowance:{allow_guest}")
            # "Continue as Guest" — go to wherever they came from, or the portal home
            if allow_guest:
                next_url = request.query_params.get('next', f'{root_path}/portal/')
                html += f'''
                            <div style="margin-top:20px; border-top:1px solid #e0e0e0; padding-top:16px; text-align:center;">
                                <a href="{next_url}"
                                   style="display:inline-block; padding:10px 24px; background:#6c757d;
                                          color:white; border-radius:5px; text-decoration:none;
                                          font-size:14px; font-weight:500;">
                                    <i class="fa fa-user-o"></i> Continue as Guest
                                </a>
                                <div style="margin-top:6px; font-size:12px; color:#999;">
                                    Public programs and API docs only
                                </div>
                            </div>
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
                <script src="{root_path}/static/energydesk/app/js/bootstrap.min.js"></script>
            </body>
            </html>
            '''
            return html

        @app.get('/auth/login/{provider}')
        async def login_provider(request: Request, provider: str):
            """Initiate OAuth flow for selected provider"""
            if provider not in self.providers:
                raise HTTPException(status_code=400, detail='Invalid provider')

            # Get root_path from X-Forwarded-Prefix header (set by Ingress)
            root_path = request.scope.get("root_path", "")

            # Build redirect URI with prefix
            # request.url_for gives us the path without prefix, so we need to add it
            base_redirect_uri = str(request.url_for('authorize', provider=provider))

            # If there's a root_path, we need to build the full URL manually
            if root_path:
                # Get the scheme from X-Forwarded-Proto header (Ingress sets this to https)
                # The internal request.url.scheme will be http (pod-to-pod), but external is https
                scheme = request.headers.get('X-Forwarded-Proto', request.url.scheme)
                netloc = request.url.netloc
                redirect_uri = f"{scheme}://{netloc}{root_path}/auth/authorize/{provider}"
                logger.info(f"OAuth redirect URI with prefix: {redirect_uri} (scheme from X-Forwarded-Proto: {scheme})")
            else:
                redirect_uri = base_redirect_uri
                logger.info(f"OAuth redirect URI (no prefix): {redirect_uri}")

            return await self.providers[provider].authorize_redirect(request, redirect_uri)

        @app.get('/auth/authorize/{provider}')
        async def authorize(request: Request, provider: str):
            """Handle OAuth callback"""
            if provider not in self.providers:
                raise HTTPException(status_code=400, detail='Invalid provider')

            try:
                token = await self.providers[provider].authorize_access_token(request)
            except Exception as e:
                logger.error(f"Error authorizing with {provider}: {e}")
                raise HTTPException(status_code=401, detail=f'Authorization failed: {str(e)}')

            # Get user info
            try:
                # For django provider, manually call the userinfo endpoint to ensure correct URL
                if provider == 'django':
                    import httpx
                    provider_config = self.config.get(provider, {})
                    userinfo_url = provider_config.get('base_url', '').rstrip('/') + provider_config.get('userinfo_endpoint', '/oauth_edesk/userinfo/')
                    logger.info(f"[DJANGO] Manually calling userinfo endpoint: {userinfo_url}")
                    headers = {'Authorization': f"Bearer {token['access_token']}"}
                    async with httpx.AsyncClient() as client:
                        response = await client.get(userinfo_url, headers=headers)
                        logger.info(f"[DJANGO] Userinfo response status: {response.status_code}")
                        response.raise_for_status()
                        user_info = response.json()
                    logger.info(f"[DJANGO] Userinfo received: {user_info}")
                elif provider == 'google':
                    user_info = token.get('userinfo')
                    if not user_info:
                        user_info = await self.providers[provider].userinfo(token=token)
                else:
                    user_info = await self.providers[provider].userinfo(token=token)
            except Exception as e:
                logger.error(f"Error getting user info from {provider}: {e}")
                raise HTTPException(status_code=401, detail=f'Failed to get user info: {str(e)}')

            # Store user info in session.
            # IMPORTANT: Azure/Google JWT access tokens are very large (often >2KB).
            # Storing them directly in the session cookie would push it over the
            # 4096-byte browser limit, silently dropping the cookie and breaking
            # the session. Instead we keep ALL access tokens in a server-side
            # in-memory store (keyed by sub) and only put a 'token_ref' (= sub)
            # in the lightweight session cookie. get_current_user_role() resolves
            # the actual token from the store when needed.
            sub = user_info.get('sub', '')
            access_token = token.get('access_token')
            if access_token and sub:
                with _token_store_lock:
                    _token_store[sub] = access_token
                logger.debug(f"Stored access_token server-side for sub={sub} provider={provider}")

            session_data = {
                'provider': provider,
                'email': user_info.get('email'),
                'name': user_info.get('name', user_info.get('given_name', '')),
                'sub': sub,
                'authenticated': True,
                'token_ref': sub,  # reference key into _token_store
            }
            # Also keep the token in-session for Django (small token, backward compat)
            if provider == 'django':
                session_data['access_token'] = access_token

            # Application-level gate (e.g. registration check).
            # If a hook is registered and returns a Response, the session is NOT
            # written — the user stays as an anonymous guest and sees whatever
            # the hook redirects to (e.g. portal home with an error notice).
            if self.post_auth_hook is not None:
                override = self.post_auth_hook(request, session_data)
                if override is not None:
                    logger.info(
                        f"post_auth_hook blocked session for {session_data.get('email')}"
                    )
                    return override

            request.session['user'] = session_data

            logger.info(f"User {user_info.get('email')} authenticated via {provider}")

            # Redirect to the original page or dashboard
            root_path = request.scope.get("root_path", "")
            return RedirectResponse(url=f'{root_path}/portal/')

        @app.get('/auth/logout')
        async def logout(request: Request):
            """Clear session and return to portal as guest"""
            request.session.clear()
            root_path = request.scope.get("root_path", "")
            return RedirectResponse(url=f'{root_path}/portal/')

        @app.get('/auth/profile', response_class=HTMLResponse)
        async def profile(request: Request):
            """Display user profile (protected route example)"""
            user = request.session.get('user')
            root_path = request.scope.get("root_path", "")
            if not user:
                return RedirectResponse(url=f'{root_path}/auth/login')

            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Profile - Clearing Service</title>
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
                        <span class="value">{user['provider']}</span>
                    </div>
                    <div class="info">
                        <span class="label">Name:</span>
                        <span class="value">{user['name']}</span>
                    </div>
                    <div class="info">
                        <span class="label">Email:</span>
                        <span class="value">{user['email']}</span>
                    </div>
                    <div class="info">
                        <span class="label">Subject ID:</span>
                        <span class="value">{user['sub']}</span>
                    </div>
                    <a href="{root_path}/auth/logout" class="logout-btn">Logout</a>
                </div>
            </body>
            </html>
            '''

    def set_post_auth_hook(self, hook: Callable) -> None:
        """
        Register an application-level gate that runs after OAuth succeeds but
        *before* the session is written.

        The hook is called as ``hook(request, session_data_dict)`` where
        ``session_data_dict`` is the dict that *would* be stored in the session.

        Return values
        -------------
        ``None``
            Proceed normally — write the session and redirect to the portal.
        A ``Response`` (e.g. ``RedirectResponse``)
            Abort the login.  The session is **not** written, so the user
            continues as an anonymous guest.  Typically redirect to the portal
            home with a query param like ``?auth_error=not_registered``.

        Example (registration gate in server.py)::

            def _check_registered(request, session_user):
                from flexgateway.authorization import lookup_user
                from flexgateway.database.session import SessionLocal
                email = (session_user.get("email") or "").lower()
                db = SessionLocal()
                try:
                    if lookup_user(email, db) is not None:
                        return None   # registered → proceed
                finally:
                    db.close()
                from urllib.parse import quote
                from starlette.responses import RedirectResponse
                root = request.scope.get("root_path", "")
                return RedirectResponse(
                    f"{root}/portal/?auth_error=not_registered&email={quote(email)}"
                )

            oidc_auth.set_post_auth_hook(_check_registered)
        """
        self.post_auth_hook = hook
        logger.info("post_auth_hook registered on FastAPIOIDCAuth")

    def get_current_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """Dependency to get current authenticated user"""
        user = request.session.get('user')
        if not user or not user.get('authenticated'):
            return None
        return user

    def get_current_user_role(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Dependency to get current authenticated user's ETRM role information

        The backend authenticates Django OAuth tokens but authorizes users from all providers
        (Azure, Google, Django) by looking up their email in the ETRM user database.

        Returns:
            Dict with role_pk, role_name, and email if authorization successful,
            None otherwise
        """
        user = self.get_current_user(request)
        if not user:
            return None

        # Resolve access token: prefer in-session token (Django, backward compat),
        # then fall back to server-side token store via token_ref (Azure/Google).
        token = user.get('access_token')
        if not token:
            token_ref = user.get('token_ref') or user.get('sub')
            if token_ref:
                with _token_store_lock:
                    token = _token_store.get(token_ref)
        if not token:
            logger.error(f"No access token found for user {user.get('email')} (provider: {user.get('provider')})")
            return None

        try:
            role_pk, role_name = authorize_user_etrm(token)
            if role_pk is None or role_name is None:
                logger.warning(f"No ETRM role found for user {user.get('email')} (provider: {user.get('provider')})")
                return None

            return {
                'role_pk': role_pk,
                'role_name': role_name,
                'email': user.get('email'),
                'provider': user.get('provider')
            }
        except Exception as e:
            logger.error(f"Error getting ETRM role for user {user.get('email')} (provider: {user.get('provider')}): {e}")
            return None

    def require_auth(self, request: Request) -> Dict[str, Any]:
        """Dependency to require authentication - raises exception if not authenticated"""
        user = self.get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def optional_auth(self, request: Request) -> Optional[Dict[str, Any]]:
        """Dependency for optional authentication - returns None if not authenticated"""
        return self.get_current_user(request)


# Helper function to build OIDC config from environment variables
def get_oidc_config_from_env() -> Dict[str, Any]:
    """
    Build OIDC configuration dictionary from environment variables

    This function reads configuration directly from environment variables
    and returns a config dictionary that can be used to initialize FastAPIOIDCAuth.

    Environment variables:
        AZURE_CLIENT_ID: Azure AD client ID
        AZURE_CLIENT_SECRET: Azure AD client secret
        AZURE_TENANT: Azure AD tenant ID (defaults to 'common')
        GOOGLE_CLIENT_ID: Google OAuth client ID
        GOOGLE_CLIENT_SECRET: Google OAuth client secret
        DJANGO_CLIENT_ID: Django OAuth Toolkit client ID
        DJANGO_CLIENT_SECRET: Django OAuth Toolkit client secret
        DJANGO_BASE_URL: Django OAuth base URL
        DJANGO_AUTHORIZATION_ENDPOINT: Django OAuth authorization endpoint (default: /o/authorize/)
        DJANGO_TOKEN_ENDPOINT: Django OAuth token endpoint (default: /o/token/)
        DJANGO_USERINFO_ENDPOINT: Django OAuth userinfo endpoint (default: /o/userinfo/)
        DJANGO_JWKS_URI: Django OAuth JWKS URI (default: /o/.well-known/jwks.json)

    Returns:
        Dictionary with provider configurations, ready to pass to FastAPIOIDCAuth

    Example:
        from energydeskapi.auth.auth_fastapi import get_oidc_config_from_env, FastAPIOIDCAuth

        oidc_config = get_oidc_config_from_env()
        if oidc_config:
            oidc_auth = FastAPIOIDCAuth("My App", app, oidc_config, secret_key=secret_key)
    """
    config = {}

    # Azure AD configuration
    azure_client_id = os.environ.get('AZURE_CLIENT_ID')
    azure_client_secret = os.environ.get('AZURE_CLIENT_SECRET')
    if azure_client_id and azure_client_secret:
        config['azure'] = {
            'client_id': azure_client_id,
            'client_secret': azure_client_secret,
            'tenant': os.environ.get('AZURE_TENANT', 'common')
        }
        logger.info("Azure AD OIDC configuration loaded from environment")

    # Google configuration
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    if google_client_id and google_client_secret:
        config['google'] = {
            'client_id': google_client_id,
            'client_secret': google_client_secret
        }
        logger.info("Google OIDC configuration loaded from environment")

    # Django OAuth Toolkit configuration
    django_client_id = os.environ.get('DJANGO_OAUTH_CLIENT_ID')
    django_client_secret = os.environ.get('DJANGO_OAUTH_CLIENT_SECRET')
    django_base_url = os.environ.get('DJANGO_OAUTH_BASE_URL')
    if django_client_id and django_client_secret and django_base_url:
        config['django'] = {
            'client_id': django_client_id,
            'client_secret': django_client_secret,
            'base_url': django_base_url,
            'authorization_endpoint': os.environ.get('DJANGO_OAUTH_AUTHORIZATION_ENDPOINT', '/o/authorize/'),
            'token_endpoint': os.environ.get('DJANGO_OAUTH_TOKEN_ENDPOINT', '/o/token/'),
            'userinfo_endpoint': os.environ.get('DJANGO_OAUTH_USERINFO_ENDPOINT', '/oauth_edesk/userinfo/'),  # FIXED: was /o/userinfo/
            'jwks_uri': os.environ.get('DJANGO_JOAUTH_WKS_URI', '/o/.well-known/jwks.json')
        }
        logger.info("Django OAuth OIDC configuration loaded from environment")

    if not config:
        logger.warning("No OIDC providers configured in environment variables")

    return config


# Helper function to create auth instance from environment variables
def create_auth_from_env(title: str, app: FastAPI, secret_key: Optional[str] = None, allow_guest: bool = False) -> Optional[FastAPIOIDCAuth]:
    """
    Create FastAPIOIDCAuth instance from environment variables

    This is a convenience function that combines config loading and auth initialization.

    Args:
        title: Application title for the login page
        app: FastAPI application instance
        secret_key: Optional secret key for session middleware (auto-generated if not provided)
        allow_guest: Allow unauthenticated guest access (default: False)

    Returns:
        FastAPIOIDCAuth instance if any providers are configured, None otherwise

    Example:
        from energydeskapi.auth.auth_fastapi import create_auth_from_env

        oidc_auth = create_auth_from_env("My App", app, secret_key="your-secret-key", allow_guest=False)
        if oidc_auth:
            logger.info("OIDC authentication enabled")
        else:
            logger.info("OIDC authentication disabled")
    """
    config = get_oidc_config_from_env()

    if not config:
        logger.info("OIDC authentication not configured (no providers found in environment)")
        return None

    return FastAPIOIDCAuth(title, app, config, secret_key, allow_guest)


