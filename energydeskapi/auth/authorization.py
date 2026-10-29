"""
Shared authorization module for Energydesk FastAPI services.

Authentication is handled by FastAPIOIDCAuth, which supports Google, Django,
Azure AD, and any other configured OIDC provider. This module handles
*authorization* — given an already-authenticated session (any provider) it
resolves the user's role and ``is_platform_admin`` flag from the configured
user directory (backends.py: the central Django appserver by default, or a
service-owned directory with AUTH_BACKEND=local), caches the result in the session, and exposes FastAPI
dependencies that every service can use.

Flow (Google)
-------------
1. Google OIDC callback → SDK stores id_token server-side (_id_token_store)
   and writes a lightweight session cookie (email, sub, provider).
2. First request after login → authorize_session_user() calls the appserver's
   POST /api/energydesk/resolve-google-token/ with the id_token.
3. Appserver verifies the Google signature, looks up the Django Account by
   email, and returns role + is_platform_admin.

Flow (Django)
-------------
1. Django OAuth callback → SDK writes the Django-issued token directly into
   the session (session['user']['token']) — there is no separate id_token
   store for this provider.
2. First request after login → authorize_session_user() calls the appserver's
   GET /api/energydesk/get-user-profile/ with that token.
3. Appserver resolves the profile from the token's own Django auth.

Flow (Azure AD and other bearer-JWT providers)
-----------------------------------------------
1. OAuth callback → SDK stores the access token server-side (generic
   per-sub _token_store, populated for every provider) and writes a
   lightweight session cookie (email, sub, provider).
2. First request after login → authorize_session_user() calls the same
   GET /api/energydesk/get-user-profile/ endpoint the Django flow uses.
3. Appserver's JWTEnergydeskAuthentication decodes the JWT's claims
   (without verifying its signature) and looks up the Django Account by the
   email claim — see _authorize_bearer_token_session's docstring for why
   this is safe and why no separate Azure-specific verification endpoint
   is needed.

All three flows share the rest:
4. Result is cached in the session under 'appserver_profile_cache' with a
   timestamp.  Subsequent requests use the cache
   (TTL = APPSERVER_PROFILE_CACHE_TTL_SECONDS, default 300 s).
5. If the user is not found in the Django DB → AuthorizedUser.unregistered()
   is returned and the caller shows a "not registered" notice.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from fastapi import Request, HTTPException, Depends

from energydeskapi.auth.backends import get_user_directory

logger = logging.getLogger(__name__)

# Cache TTL in seconds (env-configurable, default 5 min)
_CACHE_TTL: int = int(os.getenv('APPSERVER_PROFILE_CACHE_TTL_SECONDS', '300'))
_CACHE_SESSION_KEY = 'appserver_profile_cache'
_REFRESH_SKEW_SECONDS: int = int(os.getenv('GOOGLE_TOKEN_REFRESH_SKEW_SECONDS', '60'))


# ---------------------------------------------------------------------------
# Data class returned to callers
# ---------------------------------------------------------------------------

@dataclass
class AuthorizedUser:
    """Represents a fully authenticated + authorized portal user."""
    email: str
    name: str
    role: str           # UserGroup description from Django, or '' when unregistered
    role_pk: int        # UserGroup pk, or 0 when unregistered
    is_admin: bool      # True when the user's group has is_platform_admin=True
    is_active: bool
    is_registered: bool # False when email not found in the appserver
    oauth_provider: str
    full_name: str
    raw_session: Dict[str, Any] = field(default_factory=dict)
    # True when we could not even ask the appserver whether this user is
    # registered, because the id_token needed to make that call is gone
    # (typically: server restart cleared the in-memory token store, but the
    # browser's session cookie survived). This is a *session* problem, not an
    # authorization verdict — the fix is "log in again", not "contact an
    # admin". Kept distinct from is_registered=False so callers can return
    # 401 (please re-authenticate) instead of 403 (you are not entitled).
    needs_reauth: bool = False

    @classmethod
    def unregistered(cls, session_user: Dict[str, Any]) -> "AuthorizedUser":
        """Return an AuthorizedUser for an OAuth-authenticated but unregistered email."""
        return cls(
            email=session_user.get("email", ""),
            name=session_user.get("name", ""),
            role="",
            role_pk=0,
            is_admin=False,
            is_active=False,
            is_registered=False,
            oauth_provider=session_user.get("provider", ""),
            full_name=session_user.get("name", ""),
            raw_session=session_user,
        )

    @classmethod
    def session_expired(cls, session_user: Dict[str, Any]) -> "AuthorizedUser":
        """
        Return an AuthorizedUser for a session whose id_token is unavailable
        server-side (restart cleared the in-memory store, refresh failed,
        etc). Shaped like `unregistered()` for callers that only check
        `is_registered`, but flagged with `needs_reauth=True` so callers that
        care about the distinction can send the user back through
        `/auth/login` instead of telling them to contact an admin.
        """
        user = cls.unregistered(session_user)
        user.needs_reauth = True
        return user

    @classmethod
    def from_appserver(cls, profile: Dict[str, Any], session_user: Dict[str, Any]) -> "AuthorizedUser":
        """Build an AuthorizedUser from the appserver profile dict + OAuth session dict."""
        is_platform_admin = bool(profile.get('is_platform_admin', False))
        role = profile.get('role', 'Guest')
        return cls(
            email=profile.get('username', session_user.get('email', '')),
            name=session_user.get('name', profile.get('first_name', '')),
            role=role,
            role_pk=int(profile.get('role_pk', 0)),
            is_admin=is_platform_admin,
            is_active=True,
            is_registered=True,
            oauth_provider=session_user.get('provider', 'google'),
            full_name=(
                f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
                or session_user.get('name', '')
            ),
            raw_session=session_user,
        )

    def __bool__(self) -> bool:
        """
        False for an unregistered/inactive/needs-reauth user, so every
        existing `if not auth:` / `auth and ...` check across the services —
        most of which pre-date resolve_session()/require_page_session() —
        already redirects instead of rendering a page as logged-in with an
        empty role. `get_authorized_user()` already returns None (falsy) for
        no session at all; this covers "authenticated but not registered"
        and "session expired, needs re-login" cases that previously stayed
        truthy.
        """
        return self.is_registered and self.is_active and not self.needs_reauth

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "role_pk": self.role_pk,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "is_registered": self.is_registered,
            "oauth_provider": self.oauth_provider,
            "full_name": self.full_name,
            "needs_reauth": self.needs_reauth,
        }


# ---------------------------------------------------------------------------
# Session cache helpers
# ---------------------------------------------------------------------------

def _load_cached_profile(request: Request, sub: str) -> Optional[Dict[str, Any]]:
    """Return cached appserver profile for *sub* if present and not stale."""
    cache = request.session.get(_CACHE_SESSION_KEY)
    if not cache or cache.get('sub') != sub:
        return None
    age = time.time() - float(cache.get('cached_at', 0))
    if age > _CACHE_TTL:
        logger.debug(f"[authz-cache] stale for sub={sub} (age={age:.0f}s, ttl={_CACHE_TTL}s)")
        return None
    logger.debug(f"[authz-cache] hit for sub={sub} (age={age:.0f}s)")
    return cache.get('profile')


def _store_cached_profile(request: Request, sub: str, profile: Dict[str, Any]) -> None:
    """Write an appserver profile to the session cache."""
    request.session[_CACHE_SESSION_KEY] = {
        'sub': sub,
        'cached_at': time.time(),
        'profile': profile,
    }
    logger.debug(f"[authz-cache] stored for sub={sub}")


# ---------------------------------------------------------------------------
# Core resolution
# ---------------------------------------------------------------------------

def _get_id_token(request: Request, sub: str) -> Optional[str]:
    """
    Retrieve the Google id_token from the SDK's server-side store.

    Proactively refreshes it first if it's expired or within
    _REFRESH_SKEW_SECONDS of expiring, so callers never hand a stale
    token to the appserver.
    """
    try:
        from energydeskapi.auth.auth_fastapi import (
            _id_token_store, _id_token_store_lock,
            _token_expiry_store, _token_expiry_store_lock,
            refresh_google_token,
        )
    except ImportError:
        logger.error("[authz] Cannot import token stores from SDK")
        return None

    with _token_expiry_store_lock:
        expires_at = _token_expiry_store.get(sub)

    if expires_at is not None and (expires_at - time.time()) < _REFRESH_SKEW_SECONDS:
        logger.info(
            f"[authz] id_token for sub={sub} expires in "
            f"{expires_at - time.time():.0f}s — refreshing proactively"
        )
        new_id_token = refresh_google_token(sub)
        if new_id_token:
            return new_id_token
        logger.warning(
            f"[authz] Proactive refresh failed for sub={sub} — falling back to "
            "cached (possibly stale) id_token; reactive 401 retry is the last resort"
        )

    with _id_token_store_lock:
        return _id_token_store.get(sub)

def _provider_token(
    request: Optional[Request], session_user: Dict[str, Any], sub: str, refresh: bool = True,
) -> Optional[str]:
    """
    The provider credential the SDK holds server-side for this session, or None.

    Google: the id_token from _id_token_store (refreshed first when about to expire,
    unless ``refresh`` is False).
    Django: the token the OAuth callback wrote into the session itself.
    Anything else (Azure AD, ...): the access token in the generic per-sub _token_store,
    which every provider's OAuth callback populates. A provider never reads another's store.
    """
    provider = session_user.get('provider', 'google')
    if provider == 'google':
        if not refresh:
            from energydeskapi.auth.auth_fastapi import _id_token_store, _id_token_store_lock
            with _id_token_store_lock:
                return _id_token_store.get(sub)
        return _get_id_token(request, sub)
    if provider == 'django':
        return session_user.get('token') or session_user.get('access_token')
    try:
        from energydeskapi.auth.auth_fastapi import _token_store, _token_store_lock
        with _token_store_lock:
            return _token_store.get(sub)
    except Exception as exc:
        logger.debug(f"[authz] Could not read _token_store for sub={sub}: {exc}")
        return None


def authorize_session_user(
    session_user: Dict[str, Any],
    request: Request,
) -> AuthorizedUser:
    """
    Resolve an authenticated OAuth session (Google, Django, Azure AD, or any
    other configured provider) to an AuthorizedUser.

    1. Check session cache (TTL = APPSERVER_PROFILE_CACHE_TTL_SECONDS).
    2. On cache miss: ask the configured user directory (AUTH_BACKEND, see
       backends.py). The appserver directory calls authorize_user_google() for
       a Google id_token and authorize_user_django() for a Django session
       token or any other provider's bearer JWT (Azure AD included — see
       etrm_authorize.py); the local directory calls the service's resolver.
    3. Cache successful result; return unregistered on failure/404.
    """
    email = (session_user.get('email') or '').lower()
    if not email:
        return AuthorizedUser.unregistered(session_user)

    sub = session_user.get('sub') or session_user.get('token_ref') or email

    # 1. Cache hit
    cached = _load_cached_profile(request, sub)
    if cached is not None:
        logger.debug(f"[authz] {email} resolved from session cache")
        return AuthorizedUser.from_appserver(cached, session_user)

    # 2. Directory lookup
    provider = session_user.get('provider', 'google')
    profile = get_user_directory().resolve_user(
        email=email,
        provider=provider,
        sub=sub,
        token=_provider_token(request, session_user, sub),
        name=session_user.get('name', ''),
    )

    if profile is None:
        return AuthorizedUser.session_expired(session_user)
    if profile is False:
        logger.info(f"[authz] {email} authenticated but NOT registered")
        return AuthorizedUser.unregistered(session_user)

    _store_cached_profile(request, sub, profile)
    logger.info(
        f"[authz] {email} → role={profile.get('role')}, "
        f"is_platform_admin={profile.get('is_platform_admin')}"
    )
    return AuthorizedUser.from_appserver(profile, session_user)


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

def _get_oauth_session(request: Request) -> Optional[Dict[str, Any]]:
    """Extract the raw OAuth session dict set by FastAPIOIDCAuth."""
    try:
        user = request.session.get('user')
    except (AssertionError, AttributeError):
        return None
    if not user or not user.get('authenticated'):
        return None
    return user


def get_authorized_user(request: Request) -> Optional[AuthorizedUser]:
    """
    FastAPI dependency — returns an AuthorizedUser if the request carries a
    valid OAuth session, otherwise returns None.

    Thin wrapper over session.resolve_session() — ANONYMOUS and EXPIRED both
    return None here (this function has no way to signal "expired" to a
    caller expecting Optional[AuthorizedUser]; use require_page_session or
    require_api_session directly where that distinction matters).
    """
    from energydeskapi.auth.session import resolve_session, SessionState
    resolved = resolve_session(request)
    return resolved.user if resolved.state == SessionState.VALID else None


def require_authenticated_user(request: Request) -> AuthorizedUser:
    """
    FastAPI dependency — requires a valid OAuth session.
    Redirects to /auth/login if not authenticated or expired.
    """
    from energydeskapi.auth.session import require_page_session
    return require_page_session(request)


def require_registered_user(
    auth: AuthorizedUser = Depends(require_authenticated_user),
) -> AuthorizedUser:
    """
    FastAPI dependency — requires the user to be authenticated AND registered
    (present in the Django DB with an active account).
    """
    if auth.needs_reauth:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth.is_registered or not auth.is_active:
        raise HTTPException(
            status_code=403,
            detail=(
                "Your account is not yet registered in the platform. "
                "Please contact an administrator."
            ),
        )
    return auth


def require_admin(
    auth: AuthorizedUser = Depends(require_registered_user),
) -> AuthorizedUser:
    """
    FastAPI dependency — requires is_platform_admin=True on the user's group.
    """
    if not auth.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return auth


# ---------------------------------------------------------------------------
# _check_registration factory — used by each service's server.py
# ---------------------------------------------------------------------------

def make_registration_gate(root_path_fallback: str = ""):
    """
    Return a post_auth_hook callable for FastAPIOIDCAuth.set_post_auth_hook().

    Rejects users whose email is NOT registered in the configured user
    directory (AUTH_BACKEND: the Django DB, or the service's own users) by
    redirecting them to the portal home with ?auth_error=not_registered.
    Registered users pass through transparently. Applies to every provider.

    Fails open when the directory cannot say (unreachable, no credential held
    yet); fails closed only on an explicit "not registered".

    Usage in server.py::

        from energydeskapi.auth.authorization import make_registration_gate
        if oidc_auth:
            oidc_auth.set_post_auth_hook(make_registration_gate())
    """
    def _check_registration(request, session_user):
        from urllib.parse import quote as _quote

        email = (session_user.get("email") or "").lower()
        sub = session_user.get("sub") or ""
        provider = session_user.get("provider", "unknown")

        logger.info(f"[auth-gate] ── Registration check ──────────────────────────")
        logger.info(f"[auth-gate]    email    = {email}")
        logger.info(f"[auth-gate]    sub      = {sub}")
        logger.info(f"[auth-gate]    provider = {provider}")
        logger.info(f"[auth-gate]    session keys = {list(session_user.keys())}")

        if not email:
            logger.warning(f"[auth-gate] No email claim in session — letting through")
            return None  # no email claim — let through for a clear error later

        try:
            token = _provider_token(request, session_user, sub, refresh=False)
            logger.info(f"[auth-gate]    provider token found = {bool(token)}")
            profile = get_user_directory().resolve_user(
                email=email, provider=provider, sub=sub, token=token,
                name=session_user.get("name", ""),
            )
        except Exception as exc:
            logger.warning(f"[auth-gate] directory call failed for {email}: {exc} — allowing through")
            return None  # fail open on errors

        if profile is None:
            # No credential to ask with, or the directory is unreachable. Authorization
            # dependencies will catch it on the next page load.
            logger.warning(f"[auth-gate] directory could not resolve {email} — allowing through")
            return None

        if profile is not False:
            logger.info(f"[auth-gate] ✅ {email} registered — role={profile.get('role')}, role_pk={profile.get('role_pk')}")
            return None  # registered → proceed with session creation

        root_path = request.scope.get("root_path", root_path_fallback)
        logger.info(f"[auth-gate] ❌ Rejected unregistered login attempt: {email}")
        logger.info(f"[auth-gate]    Redirecting to: {root_path}/portal/?auth_error=not_registered")
        from starlette.responses import RedirectResponse as _RR
        return _RR(
            url=f"{root_path}/portal/?auth_error=not_registered&email={_quote(email)}",
            status_code=302,
        )

    return _check_registration

