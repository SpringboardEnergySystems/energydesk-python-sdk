"""
Tests for energydeskapi.auth.backends. No network: tokens are signed with a locally
generated RSA key and the JWKS is served by an in-memory fake.

These run without the ``httpx2`` library (they never touch Starlette's TestClient's
httpx path beyond what FastAPI itself needs, via ``fastapi.testclient``).
"""
from __future__ import annotations

import asyncio
import time
import warnings

import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
pytest.importorskip("fastapi")
pytest.importorskip("authlib")

from authlib.jose import JsonWebKey, jwt  # noqa: E402
from fastapi import Depends, FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from energydeskapi.auth import backends  # noqa: E402
from energydeskapi.auth.backends import (  # noqa: E402
    BearerClaims, JwksVerifier, LocalDirectory, PodTokenVerifier, VerifierChain, require_bearer,
)

ISSUER = "https://vtn.example.test"
AUDIENCE = "flexgateway"
GOOGLE_AUD = "google-client-id.apps.googleusercontent.com"


def _run(coro):
    return asyncio.run(coro)


def _new_key(kid: str):
    return JsonWebKey.generate_key("RSA", 2048, is_private=True, options={"kid": kid})


KEY = _new_key("k1")
OTHER_KEY = _new_key("k1")          # same kid, different material: a bad signature
UNKNOWN_KEY = _new_key("rotated")   # a kid the issuer's JWKS does not (yet) publish


def _jwks(*keys):
    return {"keys": [k.as_dict(is_private=False) for k in keys]}


class FakeJwks:
    def __init__(self, *keys):
        self.document = _jwks(*keys)
        self.calls = 0

    def __call__(self, url):
        self.calls += 1
        return self.document


def _sign(key, *, iss=ISSUER, aud=AUDIENCE, exp_in=3600, extra=None):
    now = int(time.time())
    payload = {"iss": iss, "aud": aud, "sub": "client-1", "client_id": "client-1",
               "scope": "read_all write_events", "iat": now, "exp": now + exp_in}
    payload.update(extra or {})
    return jwt.encode({"alg": "RS256", "kid": key.as_dict()["kid"]}, payload, key).decode()


def _verifier(fake=None, **kw):
    fake = fake or FakeJwks(KEY)
    kw.setdefault("min_refetch_interval", 0.0)
    return JwksVerifier(ISSUER, AUDIENCE, "https://vtn.example.test/.well-known/jwks.json", fetch=fake, **kw), fake


# ---------------------------------------------------------------------------
# JwksVerifier
# ---------------------------------------------------------------------------

def test_jwks_valid_token():
    verifier, fake = _verifier()
    claims = _run(verifier.verify(_sign(KEY)))
    assert claims is not None
    assert claims.subject == "client-1" and claims.client_id == "client-1"
    assert claims.scopes == frozenset({"read_all", "write_events"})
    assert claims.issuer == ISSUER
    assert fake.calls == 1
    _run(verifier.verify(_sign(KEY)))
    assert fake.calls == 1  # second token: served from the cached JWKS


def test_jwks_bad_signature():
    verifier, _ = _verifier()
    assert _run(verifier.verify(_sign(OTHER_KEY))) is None


def test_jwks_wrong_issuer_is_not_mine_and_does_no_io():
    verifier, fake = _verifier()
    assert _run(verifier.verify(_sign(KEY, iss="https://elsewhere.test"))) is None
    assert fake.calls == 0


def test_jwks_wrong_audience():
    verifier, _ = _verifier()
    assert _run(verifier.verify(_sign(KEY, aud="someone-else"))) is None


def test_jwks_expired():
    verifier, _ = _verifier(leeway=0)
    assert _run(verifier.verify(_sign(KEY, exp_in=-60))) is None


def test_jwks_missing_exp_is_rejected():
    verifier, _ = _verifier()
    now = int(time.time())
    token = jwt.encode({"alg": "RS256", "kid": "k1"}, {"iss": ISSUER, "aud": AUDIENCE, "sub": "x", "iat": now},
                       KEY).decode()
    assert _run(verifier.verify(token)) is None


def test_jwks_opaque_token_is_not_mine():
    verifier, fake = _verifier()
    assert _run(verifier.verify("opaque-token-value")) is None
    assert fake.calls == 0


def test_jwks_hs256_token_signed_with_public_key_is_rejected():
    """The classic key-confusion attack: HS256 using the public key as the HMAC secret."""
    verifier, _ = _verifier()
    import base64, hashlib, hmac, json
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    head = b64(json.dumps({"alg": "HS256", "kid": "k1"}).encode())
    body = b64(json.dumps({"iss": ISSUER, "aud": AUDIENCE, "sub": "x", "exp": int(time.time()) + 600}).encode())
    secret = KEY.as_pem(is_private=False)
    sig = b64(hmac.new(secret, f"{head}.{body}".encode(), hashlib.sha256).digest())
    assert _run(verifier.verify(f"{head}.{body}.{sig}")) is None


def test_jwks_unknown_kid_triggers_exactly_one_refetch_then_fails():
    verifier, fake = _verifier()
    assert _run(verifier.verify(_sign(KEY))) is not None
    assert fake.calls == 1
    assert _run(verifier.verify(_sign(UNKNOWN_KEY))) is None
    assert fake.calls == 2  # one refetch, then failure


def test_jwks_refetch_picks_up_a_rotated_key():
    verifier, fake = _verifier()
    assert _run(verifier.verify(_sign(KEY))) is not None
    fake.document = _jwks(KEY, UNKNOWN_KEY)
    assert _run(verifier.verify(_sign(UNKNOWN_KEY))) is not None
    assert fake.calls == 2


def test_jwks_unknown_kid_refetch_is_rate_limited():
    verifier, fake = _verifier(min_refetch_interval=3600.0)
    assert _run(verifier.verify(_sign(KEY))) is not None
    for _ in range(3):
        assert _run(verifier.verify(_sign(UNKNOWN_KEY))) is None
    assert fake.calls == 1


def test_jwks_fetch_failure_fails_closed():
    def broken(url):
        raise RuntimeError("down")

    verifier = JwksVerifier(ISSUER, AUDIENCE, "https://x/jwks", fetch=broken)
    assert _run(verifier.verify(_sign(KEY))) is None


# ---------------------------------------------------------------------------
# PodTokenVerifier and VerifierChain
# ---------------------------------------------------------------------------

def test_pod_token_match_and_mismatch(monkeypatch):
    monkeypatch.setenv("API_INTERNAL_POD_TOKEN", "s3cret")
    verifier = PodTokenVerifier()
    claims = _run(verifier.verify("s3cret"))
    assert claims is not None and claims.scopes == frozenset({"internal"})
    assert _run(verifier.verify("wrong")) is None


def test_pod_token_unset_never_matches(monkeypatch):
    monkeypatch.delenv("API_INTERNAL_POD_TOKEN", raising=False)
    assert _run(PodTokenVerifier().verify("")) is None
    assert _run(PodTokenVerifier().verify("anything")) is None


class _Stub:
    def __init__(self, result):
        self.result, self.seen = result, []

    async def verify(self, token):
        self.seen.append(token)
        return self.result


def _claims(subject):
    return BearerClaims(subject=subject, client_id=None, scopes=frozenset(), issuer="x", expires_at=None)


def test_chain_first_match_wins_and_stops():
    first, second, third = _Stub(None), _Stub(_claims("second")), _Stub(_claims("third"))
    claims = _run(VerifierChain([first, second, third]).verify("t"))
    assert claims.subject == "second"
    assert first.seen == ["t"] and second.seen == ["t"] and third.seen == []


def test_chain_falls_through_not_mine_and_returns_none_if_nobody_claims_it():
    a, b = _Stub(None), _Stub(None)
    assert _run(VerifierChain([a, b]).verify("t")) is None
    assert a.seen == b.seen == ["t"]


def test_chain_jwks_then_pod_token(monkeypatch):
    monkeypatch.setenv("API_INTERNAL_POD_TOKEN", "pod-secret")
    verifier, _ = _verifier()
    chain = VerifierChain([verifier, PodTokenVerifier()])
    assert _run(chain.verify(_sign(KEY))).issuer == ISSUER
    assert _run(chain.verify("pod-secret")).issuer == backends.POD_TOKEN_ISSUER
    assert _run(chain.verify("nope")) is None


# ---------------------------------------------------------------------------
# require_bearer
# ---------------------------------------------------------------------------

def _app(verifier):
    app = FastAPI()

    @app.get("/open")
    async def open_(claims: BearerClaims = Depends(require_bearer(verifier=verifier))):
        return {"sub": claims.subject}

    @app.get("/orders")
    async def orders(claims: BearerClaims = Depends(require_bearer("nodes:orders", verifier=verifier))):
        return {"sub": claims.subject}

    return TestClient(app)


def test_require_bearer_paths(monkeypatch):
    monkeypatch.setenv("API_INTERNAL_POD_TOKEN", "pod-secret")
    jwks, _ = _verifier()
    client = _app(VerifierChain([jwks, PodTokenVerifier()]))

    assert client.get("/open").status_code == 401                                   # no header
    assert client.get("/open", headers={"Authorization": "Basic abc"}).status_code == 401
    r = client.get("/open", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401 and r.headers["www-authenticate"] == "Bearer"
    expired = _sign(KEY, exp_in=-3600)
    assert client.get("/open", headers={"Authorization": f"Bearer {expired}"}).status_code == 401

    ok = _sign(KEY)
    assert client.get("/open", headers={"Authorization": f"Bearer {ok}"}).status_code == 200
    assert client.get("/orders", headers={"Authorization": f"Bearer {ok}"}).status_code == 403   # lacks scope
    with_scope = _sign(KEY, extra={"scope": "nodes:orders"})
    r = client.get("/orders", headers={"Authorization": f"Bearer {with_scope}"})
    assert r.status_code == 200 and r.json() == {"sub": "client-1"}


def test_pod_token_satisfies_scopes_but_a_jwt_claiming_internal_does_not(monkeypatch):
    monkeypatch.setenv("API_INTERNAL_POD_TOKEN", "pod-secret")
    jwks, _ = _verifier()
    client = _app(VerifierChain([jwks, PodTokenVerifier()]))
    assert client.get("/orders", headers={"Authorization": "Bearer pod-secret"}).status_code == 200
    sneaky = _sign(KEY, extra={"scope": "internal"})
    assert client.get("/orders", headers={"Authorization": f"Bearer {sneaky}"}).status_code == 403


# ---------------------------------------------------------------------------
# LocalDirectory
# ---------------------------------------------------------------------------

USERS = {
    "alice@example.test": {"username": "alice@example.test", "first_name": "Alice", "last_name": "A",
                           "role": "operator", "role_pk": 0, "is_platform_admin": False},
    "gone@example.test": {"username": "gone@example.test", "role": "operator", "is_active": False},
}


def _resolver(calls=None):
    def resolve(email, provider, sub):
        if calls is not None:
            calls.append((email, provider, sub))
        return USERS.get(email)
    return resolve


def _google_dir(calls=None):
    fake = FakeJwks(KEY)
    google = JwksVerifier(list(backends.GOOGLE_ISSUERS), GOOGLE_AUD, backends.GOOGLE_JWKS_URL,
                          fetch=fake, min_refetch_interval=0.0, leeway=0)
    return LocalDirectory(_resolver(calls), google_verifier=google)


def _id_token(key=KEY, *, iss="https://accounts.google.com", aud=GOOGLE_AUD, exp_in=3600,
              email="alice@example.test", **extra):
    return _sign(key, iss=iss, aud=aud, exp_in=exp_in,
                 extra={"email": email, "email_verified": True, "sub": "g-1", **extra})


def _resolve(directory, token, *, session_email="alice@example.test", provider="google"):
    return directory.resolve_user(email=session_email, provider=provider, sub="g-1", token=token)


def test_local_registered_google_user():
    calls = []
    profile = _resolve(_google_dir(calls), _id_token())
    assert profile["role"] == "operator" and profile["username"] == "alice@example.test"
    assert calls == [("alice@example.test", "google", "g-1")]


def test_local_google_accepts_both_issuer_spellings():
    assert _resolve(_google_dir(), _id_token(iss="accounts.google.com"))


def test_local_not_registered_is_false():
    token = _id_token(email="nobody@example.test")
    assert _resolve(_google_dir(), token, session_email="nobody@example.test") is False


def test_local_inactive_resolver_result_is_not_registered():
    assert _resolve(_google_dir(), _id_token(email="gone@example.test")) is False


@pytest.mark.parametrize("token_kwargs", [
    {"key": OTHER_KEY},               # bad signature
    {"aud": "another-client-id"},     # wrong audience
    {"exp_in": -60},                  # expired
    {"iss": "https://evil.test"},     # wrong issuer
])
def test_local_google_token_failing_verification_needs_reauth(token_kwargs):
    calls = []
    assert _resolve(_google_dir(calls), _id_token(**token_kwargs)) is None
    assert calls == []  # the resolver is never consulted


def test_local_google_uses_the_verified_email_not_the_sessions():
    """A session claiming to be alice, carrying a token for nobody, must not resolve to alice."""
    calls = []
    token = _id_token(email="nobody@example.test")
    assert _resolve(_google_dir(calls), token, session_email="alice@example.test") is False
    assert calls == [("nobody@example.test", "google", "g-1")]


def test_local_google_unverified_email_claim_is_rejected():
    assert _resolve(_google_dir(), _id_token(email_verified=False)) is None


def test_local_google_without_token_needs_reauth():
    assert _resolve(_google_dir(), None) is None


def test_local_google_without_client_id_fails_closed(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    assert _resolve(LocalDirectory(_resolver()), _id_token()) is None


def test_local_resolver_error_means_cannot_say():
    def boom(email, provider, sub):
        raise RuntimeError("db down")

    assert _resolve(LocalDirectory(boom), None, provider="azure") is None


def test_local_non_google_provider_resolves_without_token():
    profile = _resolve(LocalDirectory(_resolver()), None, provider="azure")
    assert profile["role"] == "operator"


# ---------------------------------------------------------------------------
# Env wiring
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_backends(monkeypatch):
    for name in ("AUTH_BACKEND", "BEARER_VERIFIERS", "AUTH_JWKS_ISSUERS"):
        monkeypatch.delenv(name, raising=False)
    backends.reset_backends()
    yield
    backends.reset_backends()


def test_defaults_are_appserver_with_introspection_and_pod_token(clean_backends):
    assert isinstance(backends.get_user_directory(), backends.AppserverDirectory)
    kinds = [type(v) for v in backends.get_bearer_verifier().verifiers]
    assert kinds == [backends.IntrospectionVerifier, backends.PodTokenVerifier]


def test_local_backend_needs_a_registered_resolver(clean_backends, monkeypatch):
    monkeypatch.setenv("AUTH_BACKEND", "local")
    with pytest.raises(RuntimeError):
        backends.get_user_directory()
    backends.register_local_resolver(_resolver())
    assert isinstance(backends.get_user_directory(), LocalDirectory)


def test_invalid_auth_backend_is_loud(clean_backends, monkeypatch):
    monkeypatch.setenv("AUTH_BACKEND", "ldap")
    with pytest.raises(ValueError):
        backends.get_user_directory()


def test_jwks_verifiers_from_env(clean_backends, monkeypatch):
    monkeypatch.setenv("BEARER_VERIFIERS", "jwks, pod-token")
    monkeypatch.setenv("AUTH_JWKS_ISSUERS", '[{"issuer": "https://a", "audience": "x", "jwks_url": "https://a/jwks"}]')
    kinds = [type(v) for v in backends.get_bearer_verifier().verifiers]
    assert kinds == [backends.JwksVerifier, backends.PodTokenVerifier]


def test_jwks_without_issuers_or_unknown_name_is_loud(clean_backends, monkeypatch):
    monkeypatch.setenv("BEARER_VERIFIERS", "jwks")
    with pytest.raises(ValueError):
        backends.get_bearer_verifier()
    backends.reset_backends()
    monkeypatch.setenv("BEARER_VERIFIERS", "magic")
    with pytest.raises(ValueError):
        backends.get_bearer_verifier()


# ---------------------------------------------------------------------------
# Dispatch through authorize_session_user / make_registration_gate (local backend)
# ---------------------------------------------------------------------------

def _request():
    from fastapi import Request
    return Request({"type": "http", "session": {}})


@pytest.fixture
def local_backend(clean_backends, monkeypatch):
    from energydeskapi.auth import auth_fastapi
    monkeypatch.setenv("AUTH_BACKEND", "local")
    backends.register_local_resolver(_resolver())
    auth_fastapi._token_store.clear()
    auth_fastapi._id_token_store.clear()
    yield auth_fastapi
    auth_fastapi._token_store.clear()
    auth_fastapi._id_token_store.clear()


def test_authorize_session_user_uses_the_local_directory(local_backend):
    from energydeskapi.auth.authorization import authorize_session_user
    user = authorize_session_user({"provider": "azure", "sub": "s1", "email": "Alice@example.test"}, _request())
    assert user.is_registered and user.role == "operator" and user.is_admin is False


def test_authorize_session_user_local_unknown_email_is_unregistered(local_backend):
    from energydeskapi.auth.authorization import authorize_session_user
    user = authorize_session_user({"provider": "azure", "sub": "s1", "email": "x@example.test"}, _request())
    assert not user.is_registered and not user.needs_reauth


def test_registration_gate_rejects_unregistered_for_non_google_provider(local_backend):
    from energydeskapi.auth.authorization import make_registration_gate
    gate = make_registration_gate()
    request = _request()
    request.scope["root_path"] = ""
    response = gate(request, {"provider": "azure", "sub": "s1", "email": "x@example.test"})
    assert response is not None and response.status_code == 302
    assert "auth_error=not_registered" in response.headers["location"]
    assert gate(request, {"provider": "azure", "sub": "s1", "email": "alice@example.test"}) is None


def test_registration_gate_fails_open_when_the_directory_cannot_say(clean_backends, monkeypatch):
    from energydeskapi.auth.authorization import make_registration_gate

    def boom(email, provider, sub):
        raise RuntimeError("db down")

    monkeypatch.setenv("AUTH_BACKEND", "local")
    backends.register_local_resolver(boom)
    gate = make_registration_gate()
    assert gate(_request(), {"provider": "azure", "sub": "s1", "email": "alice@example.test"}) is None


def test_registration_gate_fails_open_without_a_google_id_token(local_backend):
    from energydeskapi.auth.authorization import make_registration_gate
    assert make_registration_gate()(_request(), {"provider": "google", "sub": "none", "email": "x@example.test"}) is None
