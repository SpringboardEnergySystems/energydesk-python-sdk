"""
Shared FastAPI utilities for Energydesk services.

Provides two helpers that every service needs but were previously
copy-pasted into each server.py:

  register_forwarded_prefix_middleware(app)
      Registers an HTTP middleware that reads X-Forwarded-Prefix (set by
      nginx ingress) and keeps scope["root_path"] and request.state.prefix
      in sync.  Required so that auth_fastapi builds correct OAuth redirect
      URIs and templates generate correct APP_PREFIX URLs.

  setup_oidc(title, app) -> Optional[FastAPIOIDCAuth]
      Reads ENABLE_OIDC and OIDC_SECRET_KEY from the environment and calls
      create_auth_from_env.  Returns the auth instance (or None when OIDC is
      disabled).  FastAPIOIDCAuth registers the login modal, OAuth login/
      callback routes and SessionMiddleware on the app — nothing else is
      needed per service.

Usage::

    from energydeskapi.auth.fastapi_utils import (
        register_forwarded_prefix_middleware,
        setup_oidc,
    )

    app = FastAPI(title="My Service", root_path=os.environ.get("BACKEND_ROOT_PATH", ""))
    register_forwarded_prefix_middleware(app)
    oidc_auth = setup_oidc("My Service", app)
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from energydeskapi.auth.auth_fastapi import FastAPIOIDCAuth

from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)


def register_forwarded_prefix_middleware(app: FastAPI) -> None:
    """
    Register the X-Forwarded-Prefix middleware on *app*.

    nginx ingress strips the path prefix before forwarding the request but
    sets ``X-Forwarded-Prefix`` so the service knows its public mount point.
    This middleware:

    * copies the prefix into ``scope["root_path"]`` so that
      ``auth_fastapi`` builds OAuth redirect URIs with the correct prefix
      (e.g. ``https://host/flexgateway/auth/authorize/google``).
    * stores it in ``request.state.prefix`` so Jinja templates can expose
      it as ``window.APP_PREFIX``.
    * rewrites ``scope["path"]`` when the ingress is NOT stripping the
      prefix itself (edge-case, but happens in some nginx versions).
    """

    @app.middleware("http")
    async def _forwarded_prefix(request: Request, call_next):
        prefix = request.headers.get("X-Forwarded-Prefix", "")
        if prefix:
            request.scope["root_path"] = prefix
            request.state.prefix = prefix
            path = request.url.path
            if path.startswith(f"{prefix}/"):
                # Ingress is NOT stripping the prefix — do it here.
                request.scope["path"] = path[len(prefix):]
        else:
            request.state.prefix = ""
        return await call_next(request)


def setup_oidc(title: str, app: FastAPI) -> Optional[FastAPIOIDCAuth]:
    """
    Configure OIDC authentication from environment variables.

    Reads ``ENABLE_OIDC`` and ``OIDC_SECRET_KEY`` from the environment and
    calls :func:`create_auth_from_env`.

    ``FastAPIOIDCAuth`` registers the login modal, ``/auth/login``,
    ``/auth/login/{provider}`` and ``/auth/authorize/{provider}`` routes
    plus ``SessionMiddleware`` on *app* — nothing else is needed per service.

    Returns the :class:`FastAPIOIDCAuth` instance when OIDC is active, or
    ``None`` when ``ENABLE_OIDC`` is not ``"true"``.

    .. important::
       Do **not** add ``SessionMiddleware`` manually in your server.py.
       ``FastAPIOIDCAuth`` is the sole owner of that middleware.  A duplicate
       with a different key or cookie name silently wipes the session on the
       OAuth callback, causing a CSRF state mismatch.
    """
    enable_oidc = os.environ.get("ENABLE_OIDC", "false").lower() == "true"
    if not enable_oidc:
        logger.info("OIDC disabled (ENABLE_OIDC != true)")
        return None

    try:
        from energydeskapi.auth.auth_fastapi import create_auth_from_env
        secret_key = os.environ.get("OIDC_SECRET_KEY") or None
        auth = create_auth_from_env(title, app, secret_key=secret_key)
        if auth:
            logger.info("✓ OIDC enabled for '%s'", title)
        else:
            logger.warning("⚠ OIDC enabled but no providers configured — check GOOGLE_CLIENT_ID / AZURE_CLIENT_ID")
        return auth
    except ImportError as exc:
        logger.warning("OIDC unavailable — missing dependency: %s", exc)
        return None
    except Exception as exc:
        logger.error("Error initialising OIDC: %s", exc, exc_info=True)
        return None


# ---------------------------------------------------------------------------
# ETRM API connection helpers
# ---------------------------------------------------------------------------

def get_user_bearer_token(request: Request) -> Optional[str]:
    """
    Return the logged-in user's bearer token from a Starlette/FastAPI request,
    suitable for forwarding to the EnergyDesk appserver.

    Resolution order
    ----------------
    1. **Google OIDC** — returns the Google *ID token* (a signed JWT) from the
       SDK's ``_id_token_store``.  Django validates JWTs locally via Google's
       public keys, so this works for every appserver endpoint.
       The Google *access* token (``ya29.a0…``) is opaque and Django can only
       validate it on a subset of endpoints — we never send it here.
    2. **Django / password auth** — token stored directly in
       ``session['user']['token']``.
    3. **Azure / other OIDC** — access token from the SDK's ``_token_store``
       keyed by ``sub`` / ``token_ref``.

    Returns ``None`` for anonymous or expired sessions; callers should fall
    back to the system ``ENERGYDESK_TOKEN`` via :func:`build_api_conn`.
    """
    user = (getattr(request, "session", None) or {}).get("user") or {}
    provider = user.get("provider", "")

    if provider == "google":
        sub = user.get("sub") or user.get("token_ref")
        if sub:
            try:
                from energydeskapi.auth.auth_fastapi import (
                    _id_token_store,
                    _id_token_store_lock,
                )
                with _id_token_store_lock:
                    id_token = _id_token_store.get(sub)
                if id_token:
                    logger.debug("[etrm_auth] Google ID token resolved for sub=%s…", sub[:8])
                    return id_token
                logger.warning(
                    "[etrm_auth] Google ID token not found for sub=%s… — user may need to re-login.",
                    sub[:8],
                )
            except Exception as exc:
                logger.debug("[etrm_auth] Could not retrieve Google ID token: %s", exc)

    token = user.get("token") or user.get("access_token")
    if token:
        return token

    token_ref = user.get("token_ref") or user.get("sub")
    if token_ref:
        try:
            from energydeskapi.auth.auth_fastapi import _token_store, _token_store_lock
            with _token_store_lock:
                token = _token_store.get(token_ref)
            if token:
                return token
        except Exception as exc:
            logger.debug("[etrm_auth] Could not retrieve token from _token_store: %s", exc)

    return None


def build_api_conn(bearer_token: Optional[str] = None):
    """
    Build an ``ApiConnection`` to the EnergyDesk appserver.

    bearer_token
        When supplied (e.g. from :func:`get_user_bearer_token`) uses
        ``Authorization: Bearer <token>`` — the logged-in user's Google ID
        token, Azure token, or Django access token.

        When ``None`` (background / scheduler tasks) falls back to the
        ``ENERGYDESK_TOKEN`` env var with Django ``Token`` auth.

    Usage — web request::

        token    = get_user_bearer_token(request)
        api_conn = build_api_conn(token)
        data     = SomeApi.some_method(api_conn)

    Usage — background task::

        api_conn = build_api_conn()   # system token picked up automatically
    """
    from energydeskapi.sdk.api_connection import ApiConnection
    import environ

    env = environ.Env()
    url = env.str("ENERGYDESK_URL", default=None)
    api_conn = ApiConnection(url)

    if bearer_token:
        api_conn.set_token(bearer_token, "Bearer")
        logger.debug("[etrm_auth] ApiConnection built with user Bearer token")
    else:
        api_conn.set_token(env.str("ENERGYDESK_TOKEN", default=None), "Token")
        logger.debug("[etrm_auth] ApiConnection built with system Token (background task)")

    return api_conn

