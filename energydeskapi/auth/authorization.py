"""
Shared authorization module for Energydesk FastAPI services.

Authentication is handled by Google OIDC (via FastAPIOIDCAuth).
This module handles *authorization* — given an already-authenticated Google
session it resolves the user's role and ``is_platform_admin`` flag from the
central Django appserver, caches the result in the session, and exposes
FastAPI dependencies that every service can use.

Flow
----
1. Google OIDC callback → SDK stores id_token server-side (_id_token_store)
   and writes a lightweight session cookie (email, sub, provider).
2. First request after login → authorize_session_user() calls the appserver's
   POST /api/energydesk/resolve-google-token/ with the id_token.
3. Appserver verifies the Google signature, looks up the Django Account by
   email, and returns role + is_platform_admin.
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

def authorize_session_user(
    session_user: Dict[str, Any],
    request: Request,
) -> AuthorizedUser:
    """
    Resolve an authenticated Google session to an AuthorizedUser.

    1. Check session cache (TTL = APPSERVER_PROFILE_CACHE_TTL_SECONDS).
    2. On cache miss: call appserver via authorize_user_google().
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

    # 2. Appserver lookup
    id_token = _get_id_token(request, sub)
    if not id_token:
        logger.warning(
            f"[authz] {email}: no id_token available (server-side store may have been "
            "cleared after a restart) — session needs re-authentication"
        )
        return AuthorizedUser.session_expired(session_user)

    try:
        from energydeskapi.auth.etrm_authorize import authorize_user_google
        role, role_pk, is_platform_admin = authorize_user_google(id_token)
    except Exception as exc:
        logger.error(f"[authz] appserver call failed for {email}: {exc}")
        return AuthorizedUser.unregistered(session_user)

    if role is None:
        logger.info(f"[authz] {email} authenticated but NOT registered in Django")
        return AuthorizedUser.unregistered(session_user)

    profile = {
        'username': email,
        'first_name': session_user.get('name', ''),
        'last_name': '',
        'role': role,
        'role_pk': role_pk,
        'is_platform_admin': is_platform_admin,
    }
    _store_cached_profile(request, sub, profile)
    logger.info(f"[authz] {email} → role={role}, is_platform_admin={is_platform_admin}")
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
    """
    session_user = _get_oauth_session(request)
    if not session_user:
        return None
    return authorize_session_user(session_user, request)


def require_authenticated_user(request: Request) -> AuthorizedUser:
    """
    FastAPI dependency — requires a valid OAuth session.
    Redirects to /auth/login if not authenticated.
    """
    session_user = _get_oauth_session(request)
    if not session_user:
        root_path = request.scope.get("root_path", "")
        raise HTTPException(
            status_code=307,
            headers={"Location": f"{root_path}/auth/login?next={request.url.path}"},
        )
    return authorize_session_user(session_user, request)


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

    Rejects users whose email is NOT in the Django DB by redirecting them to
    the portal home with ?auth_error=not_registered.  Registered users pass
    through transparently.

    Usage in server.py::

        from energydeskapi.auth.authorization import make_registration_gate
        if oidc_auth:
            oidc_auth.set_post_auth_hook(make_registration_gate())
    """
    def _check_registration(request, session_user):
        from urllib.parse import quote as _quote
        from energydeskapi.auth.etrm_authorize import authorize_user_google
        from energydeskapi.auth.auth_fastapi import _id_token_store, _id_token_store_lock

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

        with _id_token_store_lock:
            id_token = _id_token_store.get(sub)
            store_keys = list(_id_token_store.keys())

        logger.info(f"[auth-gate]    id_token found = {bool(id_token)}")
        logger.info(f"[auth-gate]    id_token_store has {len(store_keys)} entries")

        if not id_token:
            logger.warning(f"[auth-gate] No id_token for sub={sub} email={email} — allowing through")
            return None  # fail open; authorization deps will catch it on next page load

        try:
            logger.info(f"[auth-gate]    Calling authorize_user_google for {email} ...")
            role, role_pk, is_platform_admin = authorize_user_google(id_token)
            logger.info(f"[auth-gate]    Result: role={role}, role_pk={role_pk}, is_platform_admin={is_platform_admin}")
        except Exception as exc:
            logger.warning(f"[auth-gate] appserver call failed for {email}: {exc} — allowing through")
            return None  # fail open on network errors

        if role is not None:
            logger.info(f"[auth-gate] ✅ {email} registered — role={role}, role_pk={role_pk}")
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

