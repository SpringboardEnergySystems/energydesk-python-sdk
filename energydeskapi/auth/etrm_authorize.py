import environ
import logging
import requests
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


# Heavy SDK dependencies are imported lazily so this module stays importable
# in venvs that don't have pandas/pendulum (e.g. the flexgateway service).
def _get_users_api_profile(token: str) -> Optional[dict]:
    from energydeskapi.customers.users_api import UsersApi
    from energydeskapi.sdk.api_connection import ApiConnection
    env = environ.Env()
    api_base_url = env.str('ENERGYDESK_URL')
    api_conn = ApiConnection(api_base_url)
    api_conn.set_token(token, "Bearer")
    return UsersApi.get_user_profile(api_conn)


def authorize_user_etrm(token: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Validate an OAuth access token and return (role_pk, role_name) from the
    Django appserver.  Used by clearing-service and any service that already
    has a Django-compatible bearer token.
    """
    usrprofile = _get_users_api_profile(token)
    if usrprofile is not None:
        return usrprofile['role_pk'], usrprofile['role']
    logger.warning("authorize_user_etrm: no user profile returned from appserver")
    return None, None


def authorize_user_google(id_token: str) -> Tuple[Optional[str], Optional[int], bool]:
    """
    Resolve a Google ID token against the appserver.

    Posts the id_token to ``POST /api/energydesk/resolve-google-token/``.
    The appserver verifies the token with Google's public keys, looks up the
    Django Account by email, and returns role + is_platform_admin.

    Returns:
        (role_name, role_pk, is_platform_admin)
        All falsy (None, None, False) if user not found, token invalid, or
        appserver unreachable.
    """
    env = environ.Env()
    try:
        api_base_url = env.str('ENERGYDESK_URL').rstrip('/')
    except Exception:
        logger.error("ENERGYDESK_URL not configured — cannot resolve Google token against appserver")
        return None, None, False

    url = f"{api_base_url}/api/energydesk/resolve-google-token/"
    try:
        resp = requests.post(url, json={"id_token": id_token}, timeout=10)
        if resp.status_code == 404:
            logger.info("[appserver] resolve-google-token: user not found (404)")
            return None, None, False
        if resp.status_code == 401:
            logger.warning("[appserver] resolve-google-token: token rejected (401)")
            return None, None, False
        resp.raise_for_status()
        data = resp.json()
        role = data.get('role')
        role_pk = data.get('role_pk')
        is_platform_admin = bool(data.get('is_platform_admin', False))
        logger.info(
            f"[appserver] resolved user: role={role}, role_pk={role_pk}, "
            f"is_platform_admin={is_platform_admin}"
        )
        return role, role_pk, is_platform_admin
    except requests.RequestException as exc:
        logger.error(f"[appserver] resolve-google-token call failed: {exc}")
        return None, None, False
