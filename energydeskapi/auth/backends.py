"""
Identity backends for Energydesk FastAPI services.

Two small protocols; the Django appserver is one implementation of each, a
service-owned database is the other.

``UserDirectory``
    "Is this authenticated person one of ours, and what are they?"
    ``AppserverDirectory`` is the code ``authorization.py`` used to call directly.
    ``LocalDirectory`` calls a resolver the *service* registers; the SDK never owns a
    user table. For Google sessions it first verifies the id_token itself.

``BearerVerifier``
    "Is this bearer token valid, and for whom?"
    ``IntrospectionVerifier`` (appserver ``/o/introspect/``), ``JwksVerifier`` (any
    OIDC/OAuth issuer, verified locally) and ``PodTokenVerifier`` (the shared
    ``API_INTERNAL_POD_TOKEN``), composed by ``VerifierChain``.

Configuration (environment)::

    AUTH_BACKEND        appserver (default) | local
    BEARER_VERIFIERS    comma list, in order: introspection, jwks, pod-token
                        (default "introspection,pod-token")
    AUTH_JWKS_ISSUERS   JSON list of {"issuer", "audience", "jwks_url"} for ``jwks``
    GOOGLE_CLIENT_ID    audience of the Google id_token (local backend, Google sessions)

Every local verification checks signature, issuer, audience and expiry. Nothing here
reproduces the appserver's unsigned-claim lookup. Tokens, secrets and Authorization
headers are never logged.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Protocol, Sequence, Union, runtime_checkable

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

AUTH_BACKEND_ENV = "AUTH_BACKEND"
BEARER_VERIFIERS_ENV = "BEARER_VERIFIERS"
JWKS_ISSUERS_ENV = "AUTH_JWKS_ISSUERS"
POD_TOKEN_ENV = "API_INTERNAL_POD_TOKEN"

DEFAULT_BEARER_VERIFIERS = "introspection,pod-token"

INTERNAL_SCOPE = "internal"
POD_TOKEN_ISSUER = "pod-token"

GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

# Asymmetric algorithms only. HS* is excluded on purpose (key-confusion) and so is "none".
_ALLOWED_ALGS = ["RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384"]


# ---------------------------------------------------------------------------
# User directory
# ---------------------------------------------------------------------------

@runtime_checkable
class UserDirectory(Protocol):
    def resolve_user(
        self, *, email: str, provider: str, sub: str, token: Optional[str], name: str = "",
    ) -> Union[Dict[str, Any], bool, None]:
        """
        dict  -> profile {username, first_name, last_name, role, role_pk, is_platform_admin}
        False -> authenticated but not registered
        None  -> cannot say (needs re-authentication, or the directory is unreachable)

        ``token`` is the provider credential the SDK holds server-side for this session
        (Google id_token, Django token or the provider's access token), or None.
        """
        ...


class AppserverDirectory:
    """The Django appserver, exactly as ``authorization.py`` used to call it."""

    def resolve_user(self, *, email, provider, sub, token, name=""):
        from energydeskapi.auth import etrm_authorize  # looked up at call time (tests patch it)

        if provider == "google":
            return self._google(email, token, name)
        # Django sessions, and Azure AD / any provider whose access token is a real JWT the
        # appserver accepts on get-user-profile (authorize_user_django is that call).
        if not token:
            logger.warning(
                f"[authz] {email}: no token available for provider={provider} "
                "(server-side store may have been cleared after a restart) — "
                "session needs re-authentication"
            )
            return None
        try:
            profile = etrm_authorize.authorize_user_django(token)
        except Exception as exc:
            logger.error(f"[authz] appserver call failed for {email}: {exc}")
            return False
        return profile if profile is not None else False

    @staticmethod
    def _google(email, id_token, name):
        from energydeskapi.auth import etrm_authorize

        if not id_token:
            logger.warning(
                f"[authz] {email}: no id_token available (server-side store may have been "
                "cleared after a restart) — session needs re-authentication"
            )
            return None
        try:
            role, role_pk, is_platform_admin = etrm_authorize.authorize_user_google(id_token)
        except Exception as exc:
            logger.error(f"[authz] appserver call failed for {email}: {exc}")
            return False
        if role is None:
            return False
        return {
            "username": email,
            "first_name": name,
            "last_name": "",
            "role": role,
            "role_pk": role_pk,
            "is_platform_admin": is_platform_admin,
        }


Resolver = Callable[[str, str, str], Optional[Dict[str, Any]]]


class LocalDirectory:
    """
    A directory the service owns. ``resolver(email, provider, sub) -> dict | None``;
    None means "not registered". A dict with ``is_active`` false counts as not registered.

    For ``provider == "google"`` the session's id_token is verified here (signature against
    Google's JWKS, issuer, ``GOOGLE_CLIENT_ID`` audience, expiry) and the *verified* email
    claim is what the resolver receives. A token that fails verification yields None
    (re-authenticate); the session's own, unverified, email is never used for Google.
    Other providers' emails come from the SDK's signed session cookie, set after the OIDC
    code exchange, and need no token.
    """

    def __init__(self, resolver: Resolver, *, google_client_id: Optional[str] = None,
                 google_verifier: Optional["JwksVerifier"] = None):
        self._resolver = resolver
        self._google_client_id = google_client_id
        self._google_verifier = google_verifier

    def _google(self):
        if self._google_verifier is None:
            client_id = self._google_client_id if self._google_client_id is not None \
                else os.getenv("GOOGLE_CLIENT_ID", "")
            if not client_id:
                logger.error("[authz] GOOGLE_CLIENT_ID not set — cannot verify Google id_tokens")
                return None
            self._google_verifier = JwksVerifier(list(GOOGLE_ISSUERS), client_id, GOOGLE_JWKS_URL)
        return self._google_verifier

    def resolve_user(self, *, email, provider, sub, token, name=""):
        if provider == "google":
            if not token:
                logger.warning("[authz] no id_token for a Google session — needs re-authentication")
                return None
            verifier = self._google()
            claims = verifier.verify_sync(token) if verifier else None
            verified_email = str((claims.raw.get("email") or "") if claims else "").lower()
            if claims is None or not verified_email or claims.raw.get("email_verified") in (False, "false"):
                logger.warning("[authz] Google id_token failed verification — needs re-authentication")
                return None
            email = verified_email
            if not sub:
                sub = claims.subject
        try:
            result = self._resolver(email, provider, sub)
        except Exception as exc:
            logger.error(f"[authz] local resolver failed: {type(exc).__name__}")
            return None
        if not result or result.get("is_active") is False:
            return False
        result = dict(result)
        result.setdefault("username", email)
        result.setdefault("first_name", name)
        return result


# ---------------------------------------------------------------------------
# Bearer verification
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BearerClaims:
    subject: str                      # client_id for client-credentials tokens
    client_id: Optional[str]
    scopes: FrozenSet[str]
    issuer: str
    expires_at: Optional[float]
    raw: Dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    def has_scopes(self, required: Iterable[str]) -> bool:
        """All ``required`` scopes held. A shared pod token (scope ``internal``) holds them all,
        but only when it was verified as a pod token — a JWT claiming ``internal`` does not."""
        required = frozenset(required)
        if required <= self.scopes:
            return True
        return INTERNAL_SCOPE in self.scopes and self.issuer == POD_TOKEN_ISSUER


@runtime_checkable
class BearerVerifier(Protocol):
    async def verify(self, token: str) -> Optional[BearerClaims]:
        """Claims if the token is valid; None if it is not valid *or not this verifier's kind*."""
        ...


def _scopes(value: Any) -> FrozenSet[str]:
    if isinstance(value, str):
        return frozenset(value.split())
    if isinstance(value, (list, tuple, set, frozenset)):
        return frozenset(str(v) for v in value)
    return frozenset()


class IntrospectionVerifier:
    """The appserver's ``/o/introspect/`` (``Authorization: Token``), cached by sha256(token)."""

    DEFAULT_TTL = 300  # seconds, also the upper bound
    MIN_TTL = 30
    MAX_ENTRIES = 10000

    def __init__(self):
        self._cache: Dict[str, tuple] = {}

    @staticmethod
    def _config() -> Dict[str, str]:
        return {
            "server_url": os.getenv("ENERGYDESK_URL", "").rstrip("/"),
            "introspect_endpoint": os.getenv("OAUTH_INTROSPECT_ENDPOINT", "/o/introspect/"),
            "energydesk_token": os.getenv("ENERGYDESK_TOKEN", ""),
        }

    async def _introspect(self, token: str) -> Optional[Dict[str, Any]]:
        import httpx  # imported lazily: only the introspection path needs it

        cfg = self._config()
        if not cfg["server_url"] or not cfg["energydesk_token"]:
            logger.error("ENERGYDESK_URL/ENERGYDESK_TOKEN not configured")
            return None
        url = f"{cfg['server_url']}{cfg['introspect_endpoint']}"
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Authorization": f"Token {cfg['energydesk_token']}"}
        try:
            async with httpx.AsyncClient(timeout=10) as http:
                response = await http.post(url, data={"token": token, "token_type_hint": "access_token"},
                                           headers=headers)
            if response.status_code != 200:
                logger.warning("Introspection endpoint returned HTTP %s", response.status_code)
                return None
            body = response.json()
            return body if body.get("active", False) else None
        except Exception as exc:
            logger.error("Introspection request failed: %s", type(exc).__name__)
            return None

    async def verify(self, token: str) -> Optional[BearerClaims]:
        key = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = time.monotonic()
        cached = self._cache.get(key)
        if cached and cached[1] > now:
            return cached[0]

        info = await self._introspect(token)
        if not info:
            return None
        client_id = info.get("client_id")
        exp = info.get("exp")
        claims = BearerClaims(
            subject=str(client_id or info.get("username") or ""),
            client_id=str(client_id) if client_id else None,
            scopes=_scopes(info.get("scope")),
            issuer=str(info.get("iss") or "appserver"),
            expires_at=float(exp) if exp else None,
            raw=info,
        )
        ttl = (max(self.MIN_TTL, min(self.DEFAULT_TTL, int(float(exp) - time.time())))
               if exp else self.DEFAULT_TTL)
        if len(self._cache) >= self.MAX_ENTRIES:
            self._cache = {k: v for k, v in self._cache.items() if v[1] > now}
        if len(self._cache) < self.MAX_ENTRIES:
            self._cache[key] = (claims, now + ttl)
        return claims


class _NeedsFetch(Exception):
    """Internal: the key is not cached and looking for it requires network I/O."""


def _default_fetch(url: str) -> Dict[str, Any]:
    import requests

    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


class JwksVerifier:
    """
    Any OIDC/OAuth issuer, verified locally: signature (key chosen by ``kid`` from the issuer's
    JWKS), ``iss``, ``aud``, ``exp`` and ``nbf``. ``issuer`` may be a list for providers that
    use more than one spelling (Google).

    The JWKS is cached for ``cache_ttl`` seconds; a token with an unknown ``kid`` triggers one
    refetch (at most once per ``min_refetch_interval``) and then fails. A token that is not a
    JWT, or that names a different issuer, is "not mine": None with no network traffic. (That
    routing peek reads the *unverified* ``iss``; the verified ``iss`` is checked afterwards.)
    """

    def __init__(self, issuer: Union[str, Sequence[str]], audience: str, jwks_url: str, *,
                 cache_ttl: float = 900.0, min_refetch_interval: float = 30.0, leeway: float = 30.0,
                 fetch: Callable[[str], Dict[str, Any]] = _default_fetch):
        self.issuers = [issuer] if isinstance(issuer, str) else list(issuer)
        self.audience = audience
        self.jwks_url = jwks_url
        self._ttl = cache_ttl
        self._min_refetch = min_refetch_interval
        self._leeway = leeway
        self._fetch = fetch
        self._keys: Dict[Optional[str], Any] = {}
        self._fetched_at: Optional[float] = None   # monotonic; set on every attempt, success or not
        self._lock = threading.Lock()

    # -- key cache ----------------------------------------------------------

    def _refetch(self, now: float) -> None:
        from authlib.jose import JsonWebKey

        self._fetched_at = now
        try:
            document = self._fetch(self.jwks_url)
            keys: Dict[Optional[str], Any] = {}
            for jwk in document.get("keys", []):
                if jwk.get("use") not in (None, "sig"):
                    continue
                try:
                    keys[jwk.get("kid")] = JsonWebKey.import_key(jwk)
                except Exception:
                    logger.warning("Ignoring an unparsable key in the JWKS from %s", self.jwks_url)
            if keys:
                self._keys = keys
        except Exception as exc:
            logger.warning("JWKS fetch from %s failed: %s", self.jwks_url, type(exc).__name__)

    def _key_for(self, kid: Optional[str], allow_fetch: bool):
        with self._lock:
            now = time.monotonic()
            fresh = self._fetched_at is not None and (now - self._fetched_at) < self._ttl and bool(self._keys)
            if not fresh and not allow_fetch:
                raise _NeedsFetch
            if not fresh:
                self._refetch(now)
            key = self._lookup(kid)
            if key is None and self._fetched_at != now:
                # Unknown kid on a cached set: refetch once, but not more than once per interval.
                if now - (self._fetched_at or 0) >= self._min_refetch:
                    if not allow_fetch:
                        raise _NeedsFetch
                    self._refetch(now)
                    key = self._lookup(kid)
            return key

    def _lookup(self, kid: Optional[str]):
        if kid in self._keys:
            return self._keys[kid]
        if kid is None and len(self._keys) == 1:
            return next(iter(self._keys.values()))
        return None

    # -- verification -------------------------------------------------------

    def _verify(self, token: str, allow_fetch: bool) -> Optional[BearerClaims]:
        from authlib.jose import JsonWebToken
        from authlib.jose.errors import JoseError

        unverified = _peek_unverified(token)
        if unverified is None or unverified[1].get("iss") not in self.issuers:
            return None  # not a JWT, or someone else's: not mine
        header = unverified[0]
        alg = header.get("alg")
        if alg not in _ALLOWED_ALGS:
            return None

        key = self._key_for(header.get("kid"), allow_fetch)
        if key is None:
            logger.warning("Token from %s names an unknown signing key", unverified[1].get("iss"))
            return None
        jwk_alg = key.as_dict(add_kid=False).get("alg") if hasattr(key, "as_dict") else None
        if jwk_alg and jwk_alg != alg:
            return None

        try:
            claims = JsonWebToken(_ALLOWED_ALGS).decode(
                token, key,
                claims_options={
                    "iss": {"essential": True, "values": self.issuers},
                    "aud": {"essential": True, "values": [self.audience]},
                    "exp": {"essential": True},
                },
            )
            claims.validate(leeway=self._leeway)
        except (JoseError, ValueError, KeyError, TypeError) as exc:
            logger.info("Token from %s rejected: %s", unverified[1].get("iss"), type(exc).__name__)
            return None

        raw = dict(claims)
        client_id = raw.get("client_id")
        exp = raw.get("exp")
        return BearerClaims(
            subject=str(raw.get("sub") or client_id or ""),
            client_id=str(client_id) if client_id else None,
            scopes=_scopes(raw.get("scope", raw.get("scp"))),
            issuer=str(raw["iss"]),
            expires_at=float(exp) if exp is not None else None,
            raw=raw,
        )

    def verify_sync(self, token: str) -> Optional[BearerClaims]:
        return self._verify(token, allow_fetch=True)

    async def verify(self, token: str) -> Optional[BearerClaims]:
        try:
            return self._verify(token, allow_fetch=False)  # cached keys: no I/O, no thread hop
        except _NeedsFetch:
            return await asyncio.to_thread(self._verify, token, True)


def _peek_unverified(token: str):
    """(header, payload) of a JWT without verifying it, or None if it is not one. Routing only."""
    import base64

    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        decoded = [json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4))) for p in parts[:2]]
    except Exception:
        return None
    return (decoded[0], decoded[1]) if all(isinstance(d, dict) for d in decoded) else None


class PodTokenVerifier:
    """The shared ``API_INTERNAL_POD_TOKEN``, compared in constant time. A migration aid."""

    async def verify(self, token: str) -> Optional[BearerClaims]:
        expected = os.getenv(POD_TOKEN_ENV, "")
        if not expected or not hmac.compare_digest(token.encode("utf-8"), expected.encode("utf-8")):
            return None
        return BearerClaims(subject="internal-pod", client_id=None, scopes=frozenset({INTERNAL_SCOPE}),
                            issuer=POD_TOKEN_ISSUER, expires_at=None)


class VerifierChain:
    """First verifier that returns claims wins; None from one means "try the next"."""

    def __init__(self, verifiers: Sequence[BearerVerifier]):
        self.verifiers: List[BearerVerifier] = list(verifiers)

    async def verify(self, token: str) -> Optional[BearerClaims]:
        for verifier in self.verifiers:
            claims = await verifier.verify(token)
            if claims is not None:
                return claims
        return None


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

def _bearer_token(request: Request) -> Optional[str]:
    scheme, _, value = request.headers.get("authorization", "").partition(" ")
    return value.strip() if scheme.lower() == "bearer" and value.strip() else None


def require_bearer(*scopes: str, verifier: Optional[BearerVerifier] = None):
    """
    FastAPI dependency factory: ``Depends(require_bearer("nodes:orders"))`` returns the
    ``BearerClaims`` of a valid bearer token holding every listed scope.
    401 for a missing or invalid token, 403 for a missing scope.
    """
    required = frozenset(scopes)

    async def _dependency(request: Request) -> BearerClaims:
        token = _bearer_token(request)
        if not token:
            raise HTTPException(status_code=401, detail="Bearer token required",
                                headers={"WWW-Authenticate": "Bearer"})
        claims = await (verifier or get_bearer_verifier()).verify(token)
        if claims is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token",
                                headers={"WWW-Authenticate": "Bearer"})
        if not claims.has_scopes(required):
            raise HTTPException(status_code=403, detail="Token lacks a required scope")
        return claims

    return _dependency


# ---------------------------------------------------------------------------
# Environment wiring
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_local_resolver: Optional[Resolver] = None
_directory: Optional[UserDirectory] = None
_verifier: Optional[BearerVerifier] = None


def register_local_resolver(resolver: Resolver) -> None:
    """Called once by a service at startup (``AUTH_BACKEND=local``)."""
    global _local_resolver, _directory
    with _lock:
        _local_resolver = resolver
        _directory = None


def reset_backends() -> None:
    """Forget the cached directory and verifier (re-read env on next use). For tests."""
    global _local_resolver, _directory, _verifier
    with _lock:
        _local_resolver = _directory = _verifier = None


def get_user_directory() -> UserDirectory:
    global _directory
    with _lock:
        if _directory is None:
            backend = (os.getenv(AUTH_BACKEND_ENV) or "appserver").strip().lower()
            if backend == "appserver":
                _directory = AppserverDirectory()
            elif backend == "local":
                if _local_resolver is None:
                    raise RuntimeError("AUTH_BACKEND=local but no resolver registered: "
                                       "call register_local_resolver() at startup")
                _directory = LocalDirectory(_local_resolver)
            else:
                raise ValueError(f"{AUTH_BACKEND_ENV} must be 'appserver' or 'local', got {backend!r}")
        return _directory


def _jwks_verifiers_from_env() -> List[JwksVerifier]:
    raw = os.getenv(JWKS_ISSUERS_ENV, "").strip()
    try:
        entries = json.loads(raw) if raw else []
        return [JwksVerifier(e["issuer"], e["audience"], e["jwks_url"]) for e in entries]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"{JWKS_ISSUERS_ENV} must be a JSON list of "
                         f'{{"issuer", "audience", "jwks_url"}} objects ({type(exc).__name__})') from None


def get_bearer_verifier() -> BearerVerifier:
    global _verifier
    with _lock:
        if _verifier is None:
            names = [n.strip().lower() for n in
                     (os.getenv(BEARER_VERIFIERS_ENV) or DEFAULT_BEARER_VERIFIERS).split(",") if n.strip()]
            verifiers: List[BearerVerifier] = []
            for name in names:
                if name == "introspection":
                    verifiers.append(IntrospectionVerifier())
                elif name == "pod-token":
                    verifiers.append(PodTokenVerifier())
                elif name == "jwks":
                    jwks = _jwks_verifiers_from_env()
                    if not jwks:
                        raise ValueError(f"{BEARER_VERIFIERS_ENV} lists 'jwks' but {JWKS_ISSUERS_ENV} is empty")
                    verifiers.extend(jwks)
                else:
                    raise ValueError(f"Unknown verifier {name!r} in {BEARER_VERIFIERS_ENV}")
            _verifier = VerifierChain(verifiers)
        return _verifier
