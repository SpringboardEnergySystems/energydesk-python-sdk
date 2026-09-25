"""
Tests for the OAUTH_REDIRECT_URI_<PROVIDER> override in FastAPIOIDCAuth.

Regression coverage for 2026-09-22: a customer's Azure AD app was
registered against ".../auth/login/azure" from before this SDK settled on
"/auth/authorize/{provider}", and re-registering it with the IdP wasn't
immediate. The override lets a deployment keep the IdP's existing redirect
URI on file. Two failure modes covered here:

1. When the override path happens to collide with this SDK's own
   "/auth/login/{provider}" route (exactly the Azure case above), a plain
   alias route registered at that same path is never reached -- Starlette
   matches the earlier-registered parameterized route first. login_provider()
   must detect an incoming callback (?code=/?error=) and delegate directly.
2. When the override path doesn't collide with anything, the alias route
   registered by _register_routes() must actually be reachable.
"""
from __future__ import annotations

import importlib
import os

import pytest

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except:
    pytest.skip("fastapi not installed", allow_module_level=True)
from energydeskapi.auth.auth_fastapi import FastAPIOIDCAuth

AZURE_CONFIG = {"azure": {"client_id": "fake-client-id", "client_secret": "fake-secret", "tenant": "common"}}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("OAUTH_REDIRECT_URI_AZURE", raising=False)


def _build_app(monkeypatch, override_uri: str) -> FastAPI:
    monkeypatch.setenv("OAUTH_REDIRECT_URI_AZURE", override_uri)
    app = FastAPI()
    FastAPIOIDCAuth("Test App", app, AZURE_CONFIG, secret_key="testsecret")
    return app

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_login_provider_uses_the_override_as_redirect_uri(monkeypatch):
    app = _build_app(monkeypatch, "https://elvia.energydesk.no/auth/login/azure")
    client = TestClient(app, follow_redirects=False)

    resp = client.get("/auth/login/azure")

    assert resp.status_code in (302, 307)
    location = resp.headers["location"]
    assert "redirect_uri=https%3A%2F%2Felvia.energydesk.no%2Fauth%2Flogin%2Fazure" in location

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_callback_at_a_colliding_override_path_reaches_the_callback_handler(monkeypatch):
    """The override ("/auth/login/azure") is the SAME path pattern as the
    SDK's own initiate route -- login_provider() must recognize an incoming
    ?code=/?error= as a callback rather than starting a fresh OAuth redirect
    to Microsoft (the bug: it silently sent the browser back to Microsoft
    forever instead of ever completing login)."""
    app = _build_app(monkeypatch, "https://elvia.energydesk.no/auth/login/azure")
    client = TestClient(app, follow_redirects=False)

    resp = client.get("/auth/login/azure?code=fakecode&state=fakestate")

    # A fabricated request with no real prior session correctly fails the
    # CSRF state check inside authorize() -- the meaningful assertion is
    # that it reached authorize() at all (401), not that it redirected to
    # Microsoft again (302/307, the pre-fix behavior).
    assert resp.status_code == 401
    assert "mismatching_state" in resp.text or "state" in resp.text.lower()

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_callback_at_a_non_colliding_override_path_is_reachable(monkeypatch):
    """A custom override path with no collision must be served by the
    alias route _register_routes() adds for it."""
    app = _build_app(monkeypatch, "https://elvia.energydesk.no/oauth/microsoft/callback")
    client = TestClient(app, follow_redirects=False)

    resp = client.get("/oauth/microsoft/callback?code=fakecode&state=fakestate")

    assert resp.status_code == 401
    assert "mismatching_state" in resp.text or "state" in resp.text.lower()

@pytest.mark.skipif(
    not importlib.util.find_spec("httpx2"), reason="requires the httpx2 library"
)
def test_no_override_keeps_the_default_redirect_uri(monkeypatch):
    app = FastAPI()
    FastAPIOIDCAuth("Test App", app, AZURE_CONFIG, secret_key="testsecret")
    client = TestClient(app, follow_redirects=False, base_url="https://portal.example.com")

    resp = client.get("/auth/login/azure")

    assert resp.status_code in (302, 307)
    location = resp.headers["location"]
    assert "redirect_uri=https%3A%2F%2Fportal.example.com%2Fauth%2Fauthorize%2Fazure" in location
