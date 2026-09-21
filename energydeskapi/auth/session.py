"""
Unified session validity for Energydesk FastAPI portals.

One decision, made in one place: is this session valid, and if not, what
happens. Implements the design from
`energydesk-tradingdesk/plans/20260916-session-validity-unification.md`.

Services should use the three entry points below instead of hand-rolling
`check_auth_and_redirect` / `require_auth_portal` / ad-hoc role lookups:

    require_page_session(request)   -> AuthorizedUser   (pages: 307 to /auth/login)
    require_api_session(request)    -> AuthorizedUser    (APIs: 401/403 JSON)
    auth_template_context(request)  -> dict              (merge into template context)

`get_authorized_user` / `require_authenticated_user` / `require_registered_user`
in `authorization.py` keep working — they're now thin wrappers around
`resolve_session()` so existing callers don't break.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import quote

from fastapi import HTTPException, Request

from energydeskapi.auth.authorization import (
    AuthorizedUser,
    _get_access_token,
    _get_oauth_session,
    authorize_session_user,
)

logger = logging.getLogger(__name__)

# A trading day plus overnight — see the unification plan's open question #1
# for why 12h was picked; override per-service if a portal's users routinely
# leave tabs open longer (e.g. clearing/back-office).
SESSION_ABSOLUTE_LIFETIME_SECONDS = int(os.getenv("SESSION_ABSOLUTE_LIFETIME_SECONDS", str(12 * 3600)))
TOKEN_REFRESH_SKEW_SECONDS = int(os.getenv("TOKEN_REFRESH_SKEW_SECONDS", "60"))


class SessionState(Enum):
    ANONYMOUS = "anonymous"   # no cookie / not authenticated
    VALID = "valid"           # AuthorizedUser attached
    EXPIRED = "expired"       # cookie present but token gone/expired/unrefreshable


@dataclass
class ResolvedSession:
    state: SessionState
    user: Optional[AuthorizedUser] = None
    reason: str = ""  # for logs: token_missing, token_expired, refresh_failed, absolute_lifetime


def _token_exists_for(provider: str, sub: str, session_user: dict, request: Request) -> bool:
    if provider == 'google':
        from energydeskapi.auth.auth_fastapi import _id_token_store, _id_token_store_lock
        with _id_token_store_lock:
            return sub in _id_token_store
    return bool(_get_access_token(request, sub, session_user))


def resolve_session(request: Request) -> ResolvedSession:
    """
    Decide whether the current request carries a valid session, per the
    unification plan's §3 rules, in order:

    1. No session → ANONYMOUS.
    2. Session older than SESSION_ABSOLUTE_LIFETIME_SECONDS → EXPIRED.
    3. Provider token missing from the server-side store → EXPIRED
       (this is what a pod restart / rollout looks like today, before the
       Redis-backed store lands).
    4. Token within TOKEN_REFRESH_SKEW_SECONDS of expiring → try to refresh;
       EXPIRED on failure or when the provider has no refresh implementation.
    5. Otherwise resolve the role via authorize_session_user() → VALID.

    On EXPIRED, clears request.session so the next request is cleanly
    ANONYMOUS instead of re-hitting the same expired state.
    """
    session_user = _get_oauth_session(request)
    if not session_user:
        return ResolvedSession(state=SessionState.ANONYMOUS)

    sub = session_user.get('sub') or session_user.get('token_ref') or session_user.get('email') or ''
    provider = session_user.get('provider')

    issued_at = session_user.get('issued_at')
    if issued_at is not None and (time.time() - float(issued_at)) > SESSION_ABSOLUTE_LIFETIME_SECONDS:
        logger.info(f"[session] {session_user.get('email')}: absolute lifetime exceeded")
        request.session.clear()
        return ResolvedSession(state=SessionState.EXPIRED, reason="absolute_lifetime")

    if not _token_exists_for(provider, sub, session_user, request):
        logger.info(f"[session] {session_user.get('email')} (provider={provider}): token missing from store")
        request.session.clear()
        return ResolvedSession(state=SessionState.EXPIRED, reason="token_missing")

    from energydeskapi.auth.auth_fastapi import _token_expiry_store, _token_expiry_store_lock, refresh_token_for_provider
    with _token_expiry_store_lock:
        expires_at = _token_expiry_store.get(sub)

    if expires_at is not None and (expires_at - time.time()) < TOKEN_REFRESH_SKEW_SECONDS:
        logger.info(f"[session] {session_user.get('email')} (provider={provider}): token expiring soon, refreshing")
        refreshed = refresh_token_for_provider(provider, sub)
        if not refreshed:
            logger.info(f"[session] {session_user.get('email')} (provider={provider}): refresh failed or unsupported")
            request.session.clear()
            reason = "refresh_failed" if provider == 'google' else "token_expired"
            return ResolvedSession(state=SessionState.EXPIRED, reason=reason)

    user = authorize_session_user(session_user, request)
    return ResolvedSession(state=SessionState.VALID, user=user)


def require_page_session(request: Request) -> AuthorizedUser:
    """
    FastAPI dependency for page routes. ANONYMOUS/EXPIRED redirect (307) to
    /auth/login, with ?reason=expired set so the login page can explain why.
    """
    resolved = resolve_session(request)
    if resolved.state != SessionState.VALID:
        root_path = request.scope.get("root_path", "")
        next_url = quote(request.url.path)
        location = f"{root_path}/auth/login?next={next_url}"
        if resolved.state == SessionState.EXPIRED:
            location += "&reason=expired"
        raise HTTPException(status_code=307, headers={"Location": location})
    return resolved.user


def require_api_session(request: Request) -> AuthorizedUser:
    """
    FastAPI dependency for API/proxy routes. ANONYMOUS/EXPIRED → 401 JSON
    with a `code` the frontend can branch on; VALID-but-unregistered → 403.
    """
    resolved = resolve_session(request)
    if resolved.state == SessionState.ANONYMOUS:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Not authenticated.", "code": "not_authenticated"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if resolved.state == SessionState.EXPIRED:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Your session has expired.", "code": "session_expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = resolved.user
    if not user.is_registered or not user.is_active:
        raise HTTPException(status_code=403, detail={"detail": "Not registered.", "code": "not_registered"})
    return user


def auth_template_context(request: Request) -> dict:
    """
    FastAPI dependency for page template contexts. Always the same keys —
    services merge this into their own context dict instead of assembling
    auth/user/provider info by hand.
    """
    resolved = resolve_session(request)
    auth = resolved.user if resolved.state == SessionState.VALID else None
    raw_user = request.session.get('user') if resolved.state != SessionState.ANONYMOUS else None

    from energydeskapi.auth.auth_fastapi import get_active_oidc_auth
    oidc_auth = get_active_oidc_auth()
    available_providers = []
    if oidc_auth is not None:
        root_path = request.scope.get("root_path", "")
        available_providers = [
            {
                'key': key,
                'name': oidc_auth.PROVIDER_CONFIGS[key]['display_name'],
                'login_url': f'{root_path}/auth/login/{key}',
            }
            for key in oidc_auth.providers.keys()
        ]

    return {
        "auth": auth,
        "user": raw_user,
        "anonymous_only": os.environ.get("ANONYMOUS_ONLY", "false").lower() == "true",
        "available_providers": available_providers,
    }
