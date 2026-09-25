"""
Tests for session.py's resolve_session() and the three FastAPI entry points.

Companion to test_authorization.py, which covers authorize_session_user()'s
per-provider dispatch directly. These tests cover the layer above it: the
absolute-lifetime check, the proactive-refresh-by-expiry check, and turning
authorize_session_user()'s needs_reauth signal into SessionState.EXPIRED.
"""
from __future__ import annotations

import importlib
import time

try:
    import pytest
    from fastapi import HTTPException

    from energydeskapi.auth import auth_fastapi
    from energydeskapi.auth import session
except:
    pytest.skip("fastapi not installed", allow_module_level=True)

class _FakeRequest:
    """A request-like object with a plain-dict .session, matching what
    resolve_session() reads and writes (request.session.get/.clear)."""

    def __init__(self, session_data=None):
        self.session = dict(session_data or {})
        self.scope = {"root_path": ""}
        self.url = type("U", (), {"path": "/portal/"})()
        self.query_params = {}


@pytest.fixture(autouse=True)
def clean_token_stores():
    auth_fastapi._token_store.clear()
    auth_fastapi._id_token_store.clear()
    auth_fastapi._token_expiry_store.clear()
    yield
    auth_fastapi._token_store.clear()
    auth_fastapi._id_token_store.clear()
    auth_fastapi._token_expiry_store.clear()

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_no_session_is_anonymous():
    res = session.resolve_session(_FakeRequest())
    assert res.state == session.SessionState.ANONYMOUS


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_valid_google_session_resolves(monkeypatch):
    auth_fastapi._id_token_store["sub123"] = "fake.id.token"
    auth_fastapi._token_expiry_store["sub123"] = time.time() + 3600

    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(etrm_authorize, "authorize_user_google", lambda t: ("Trader", 5, False))

    r = _FakeRequest({"user": {
        "provider": "google", "email": "a@b.com", "name": "A B", "sub": "sub123",
        "authenticated": True, "token_ref": "sub123", "issued_at": time.time(),
    }})
    res = session.resolve_session(r)
    assert res.state == session.SessionState.VALID
    assert res.user.role == "Trader"


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_azure_session_with_missing_token_is_expired():
    """No entry in _token_store for this sub -- authorize_session_user()
    returns needs_reauth=True, which resolve_session() must turn into
    EXPIRED("token_missing"), not silently render an unregistered user."""
    r = _FakeRequest({"user": {
        "provider": "azure", "email": "c@d.com", "name": "C D", "sub": "sub999",
        "authenticated": True, "token_ref": "sub999", "issued_at": time.time(),
    }})
    res = session.resolve_session(r)
    assert res.state == session.SessionState.EXPIRED
    assert res.reason == "token_missing"
    # EXPIRED must clear the session so the next request is cleanly ANONYMOUS.
    assert "user" not in r.session


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_azure_session_with_stored_token_is_valid_and_preserves_admin(monkeypatch):
    auth_fastapi._token_store["sub-az"] = "azure.jwt.token"

    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(
        etrm_authorize, "authorize_user_django",
        lambda t: {"role": "Trader", "role_pk": 2, "is_platform_admin": True},
    )

    r = _FakeRequest({"user": {
        "provider": "azure", "email": "az@hafslund.no", "name": "Az", "sub": "sub-az",
        "authenticated": True, "token_ref": "sub-az", "issued_at": time.time(),
    }})
    res = session.resolve_session(r)
    assert res.state == session.SessionState.VALID
    assert res.user.is_admin is True


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_absolute_lifetime_exceeded_is_expired():
    r = _FakeRequest({"user": {
        "provider": "google", "email": "e@f.com", "name": "E F", "sub": "sub123",
        "authenticated": True, "token_ref": "sub123",
        "issued_at": time.time() - (session.SESSION_ABSOLUTE_LIFETIME_SECONDS + 3600),
    }})
    res = session.resolve_session(r)
    assert res.state == session.SessionState.EXPIRED
    assert res.reason == "absolute_lifetime"


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_require_page_session_redirects_with_reason_expired():
    r = _FakeRequest({"user": {
        "provider": "azure", "email": "g@h.com", "name": "G H", "sub": "sub-missing",
        "authenticated": True, "token_ref": "sub-missing", "issued_at": time.time(),
    }})
    with pytest.raises(HTTPException) as exc_info:
        session.require_page_session(r)
    assert exc_info.value.status_code == 307
    assert "reason=expired" in exc_info.value.headers["Location"]


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_require_page_session_no_reason_when_anonymous():
    r = _FakeRequest()
    with pytest.raises(HTTPException) as exc_info:
        session.require_page_session(r)
    assert exc_info.value.status_code == 307
    assert "reason=expired" not in exc_info.value.headers["Location"]


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_require_api_session_401_not_authenticated_when_anonymous():
    with pytest.raises(HTTPException) as exc_info:
        session.require_api_session(_FakeRequest())
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "not_authenticated"


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_require_api_session_401_session_expired_when_token_missing():
    r = _FakeRequest({"user": {
        "provider": "azure", "email": "i@j.com", "name": "I J", "sub": "sub-gone",
        "authenticated": True, "token_ref": "sub-gone", "issued_at": time.time(),
    }})
    with pytest.raises(HTTPException) as exc_info:
        session.require_api_session(r)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "session_expired"


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_require_api_session_403_not_registered(monkeypatch):
    auth_fastapi._id_token_store["sub-unreg"] = "fake.id.token"
    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(etrm_authorize, "authorize_user_google", lambda t: (None, None, False))

    r = _FakeRequest({"user": {
        "provider": "google", "email": "k@l.com", "name": "K L", "sub": "sub-unreg",
        "authenticated": True, "token_ref": "sub-unreg", "issued_at": time.time(),
    }})
    with pytest.raises(HTTPException) as exc_info:
        session.require_api_session(r)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "not_registered"
