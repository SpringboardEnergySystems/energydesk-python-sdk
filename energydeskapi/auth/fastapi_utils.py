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

