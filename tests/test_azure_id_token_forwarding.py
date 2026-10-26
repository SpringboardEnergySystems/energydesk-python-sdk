"""get_user_bearer_token forwards the verifiable Azure ID token, not the Graph access token."""
from types import SimpleNamespace

import pytest

from energydeskapi.auth import auth_fastapi
from energydeskapi.auth.fastapi_utils import get_user_bearer_token

SUB = "azure-sub-123456"


def _request(provider: str, **user):
    return SimpleNamespace(session={"user": {"provider": provider, "sub": SUB, "token_ref": SUB, **user}})


@pytest.fixture(autouse=True)
def _clean_stores():
    for store in (auth_fastapi._token_store, auth_fastapi._id_token_store):
        store.clear()
    yield
    for store in (auth_fastapi._token_store, auth_fastapi._id_token_store):
        store.clear()


def test_azure_session_forwards_the_id_token_not_the_graph_access_token():
    auth_fastapi._token_store[SUB] = "graph-access-token"
    auth_fastapi._id_token_store[SUB] = "azure-id-token"
    assert get_user_bearer_token(_request("azure")) == "azure-id-token"


def test_azure_session_without_a_stored_id_token_falls_back_to_the_access_token():
    """Sessions created before this change keep working until the user logs in again."""
    auth_fastapi._token_store[SUB] = "graph-access-token"
    assert get_user_bearer_token(_request("azure")) == "graph-access-token"


def test_django_session_is_unchanged():
    auth_fastapi._id_token_store[SUB] = "should-not-be-used"
    assert get_user_bearer_token(_request("django", access_token="django-token")) == "django-token"


def test_google_session_still_forwards_the_id_token():
    auth_fastapi._id_token_store[SUB] = "google-id-token"
    assert get_user_bearer_token(_request("google")) == "google-id-token"
