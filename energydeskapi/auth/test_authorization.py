"""
Tests for authorize_session_user()'s per-provider dispatch.

Regression coverage for 2026-09-21: Azure AD (and any other non-Google,
non-Django provider) fell into _authorize_google_session, which only reads
_id_token_store -- a store only Google's OAuth callback ever populates.
Every Azure-authenticated session was permanently treated as needing
re-auth, even immediately after a successful login, because the real
token lives in the generic per-sub _token_store instead. Confirmed live
against Celsio/Hafslund's Azure-authenticated users in energydesk-insight.
"""
from __future__ import annotations

import importlib
from unittest.mock import MagicMock

import pytest
from fastapi import Request

from energydeskapi.auth import authorization as authz
from energydeskapi.auth import auth_fastapi


def _fake_request() -> Request:
    """A Request whose .session is a plain dict, matching what
    _load_cached_profile/_store_cached_profile read and write."""
    scope = {"type": "http", "session": {}}
    return Request(scope)


@pytest.fixture(autouse=True)
def clean_token_stores():
    auth_fastapi._token_store.clear()
    auth_fastapi._id_token_store.clear()
    yield
    auth_fastapi._token_store.clear()
    auth_fastapi._id_token_store.clear()

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_azure_session_resolves_via_the_generic_token_store(monkeypatch):
    """The real fix: an Azure session's token lives in _token_store (by
    sub), not _id_token_store (Google-only) -- and gets sent to the same
    appserver endpoint _authorize_django_session already uses."""
    auth_fastapi._token_store["azure-sub-1"] = "azure-jwt-abc"

    captured = {}

    def fake_authorize_user_django(token):
        captured["token"] = token
        return {"role": "Trader", "is_platform_admin": False}

    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(etrm_authorize, "authorize_user_django", fake_authorize_user_django)

    user = authz.authorize_session_user(
        {"provider": "azure", "sub": "azure-sub-1", "email": "user@hafslund.no"},
        _fake_request(),
    )

    assert captured["token"] == "azure-jwt-abc"
    assert user.is_registered is True
    assert user.role == "Trader"
    assert user.needs_reauth is False

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_azure_session_with_no_stored_token_needs_reauth(monkeypatch):
    """Confirmed live: not present -- this must resolve to session_expired
    (needs_reauth=True, a 401 "please log in again"), not silently
    authorize as some other identity or raise."""
    user = authz.authorize_session_user(
        {"provider": "azure", "sub": "azure-sub-missing", "email": "user@hafslund.no"},
        _fake_request(),
    )
    assert user.needs_reauth is True
    assert user.is_registered is False

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_azure_session_never_reads_the_google_only_id_token_store(monkeypatch):
    """Even if a (mismatched, coincidental) value sits in _id_token_store
    under the same sub, an Azure session must not use it -- that store is
    exclusively populated by Google's own OAuth callback."""
    auth_fastapi._id_token_store["azure-sub-2"] = "this-is-a-google-id-token-not-azures"

    def fail_if_called(id_token):
        raise AssertionError("authorize_user_google must never be called for an azure session")

    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(etrm_authorize, "authorize_user_google", fail_if_called)

    user = authz.authorize_session_user(
        {"provider": "azure", "sub": "azure-sub-2", "email": "user@hafslund.no"},
        _fake_request(),
    )
    # No token in the *correct* store (_token_store) for this sub, so this
    # must still be session_expired, not a lookup against the wrong store.
    assert user.needs_reauth is True


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_django_session_dispatch_is_unaffected_by_the_azure_branch(monkeypatch):
    captured = {}

    def fake_authorize_user_django(token):
        captured["token"] = token
        return {"role": "Admin", "is_platform_admin": True}

    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(etrm_authorize, "authorize_user_django", fake_authorize_user_django)

    user = authz.authorize_session_user(
        {"provider": "django", "sub": "django-sub-1", "email": "user@celsio.no", "token": "django-token-xyz"},
        _fake_request(),
    )
    assert captured["token"] == "django-token-xyz"
    assert user.is_registered is True


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_google_session_dispatch_is_unaffected_by_the_azure_branch(monkeypatch):
    """Google still resolves via _id_token_store, exactly as before --
    the new elif branch must not have changed this path's behaviour."""
    auth_fastapi._id_token_store["google-sub-1"] = "google-id-token-jwt"
    monkeypatch.setattr(auth_fastapi, "_token_expiry_store", {}, raising=False)

    captured = {}

    def fake_authorize_user_google(id_token):
        captured["id_token"] = id_token
        return "Viewer", 3, False

    import energydeskapi.auth.etrm_authorize as etrm_authorize
    monkeypatch.setattr(etrm_authorize, "authorize_user_google", fake_authorize_user_google)

    user = authz.authorize_session_user(
        {"provider": "google", "sub": "google-sub-1", "email": "user@gmail.com"},
        _fake_request(),
    )
    assert captured["id_token"] == "google-id-token-jwt"
    assert user.is_registered is True


@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_default_provider_unset_still_treated_as_google():
    """authorize_session_user()'s own default is provider='google' when the
    session carries none at all -- unaffected by adding the azure branch,
    since it's an elif on 'google' specifically, not a bare else."""
    user = authz.authorize_session_user(
        {"sub": "no-provider-sub", "email": "user@example.com"},
        _fake_request(),
    )
    # No id_token stored for this sub either -- same as before this fix,
    # this must be session_expired via the google path, not the new azure one.
    assert user.needs_reauth is True
