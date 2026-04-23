import environ
import logging
import requests
from typing import Optional, Tuple
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.sdk.api_connection import ApiConnection
logger = logging.getLogger(__name__)


# Heavy SDK dependencies are imported lazily so this module stays importable
# in venvs that don't have pandas/pendulum (e.g. the flexgateway service).
def _get_users_api_profile(token: str) -> Optional[dict]:
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
    logger.info(f"[authorize_user_etrm] Received token: {token[:20]}... (length: {len(token)})")
    
    # Check if it's a JWT (has 3 parts separated by dots)
    is_jwt = token.count('.') == 2
    logger.info(f"[authorize_user_etrm] Token format: {'JWT' if is_jwt else 'Opaque'}")
    
    # If it's a JWT, try to decode the header to see the issuer
    if is_jwt:
        try:
            import base64
            import json
            # Decode header (first part before first dot)
            header_b64 = token.split('.')[0]
            # Add padding if needed
            header_b64 += '=' * (4 - len(header_b64) % 4)
            header = json.loads(base64.urlsafe_b64decode(header_b64))
            logger.info(f"[authorize_user_etrm] JWT header: {header}")
            
            # Decode payload (second part)
            payload_b64 = token.split('.')[1]
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            logger.info(f"[authorize_user_etrm] JWT payload (issuer): {payload.get('iss', 'N/A')}")
            logger.info(f"[authorize_user_etrm] JWT payload (audience): {payload.get('aud', 'N/A')}")
            logger.info(f"[authorize_user_etrm] JWT payload (email): {payload.get('email', 'N/A')}")
        except Exception as e:
            logger.warning(f"[authorize_user_etrm] Failed to decode JWT: {e}")
    
    usrprofile = _get_users_api_profile(token)
    if usrprofile is not None:
        logger.info(f"[authorize_user_etrm] User profile found: {usrprofile}")
        return usrprofile['role_pk'], usrprofile['role']
    logger.warning("[authorize_user_etrm] No user profile returned from appserver")
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
    except Exception as exc:
        logger.error(f"[appserver] ❌ ENERGYDESK_URL not configured — cannot resolve Google token: {exc}")
        return None, None, False

    url = f"{api_base_url}/api/energydesk/resolve-google-token/"
    token_preview = id_token[:20] + "..." if id_token and len(id_token) > 20 else id_token
    logger.info(f"[appserver] 🔍 Resolving Google token against appserver")
    logger.info(f"[appserver]    ENERGYDESK_URL = {api_base_url}")
    logger.info(f"[appserver]    POST {url}")
    logger.info(f"[appserver]    id_token preview = {token_preview} (len={len(id_token) if id_token else 0})")

    try:
        resp = requests.post(url, json={"id_token": id_token}, timeout=10)
        logger.info(f"[appserver]    Response status: {resp.status_code}")
        logger.info(f"[appserver]    Response headers: {dict(resp.headers)}")
        try:
            response_body = resp.text[:500]  # cap at 500 chars to avoid flooding logs
            logger.info(f"[appserver]    Response body (first 500 chars): {response_body}")
        except Exception:
            pass

        if resp.status_code == 404:
            logger.info("[appserver] resolve-google-token: user not found (404) — user is NOT registered in Django DB")
            return None, None, False
        if resp.status_code == 401:
            logger.warning("[appserver] resolve-google-token: token rejected (401) — id_token may be expired or invalid")
            return None, None, False
        resp.raise_for_status()
        data = resp.json()
        role = data.get('role')
        role_pk = data.get('role_pk')
        is_platform_admin = bool(data.get('is_platform_admin', False))
        logger.info(
            f"[appserver] ✅ resolved user: role={role}, role_pk={role_pk}, "
            f"is_platform_admin={is_platform_admin}"
        )
        logger.info(f"[appserver]    Full response data: {data}")
        return role, role_pk, is_platform_admin
    except requests.RequestException as exc:
        logger.error(f"[appserver] ❌ resolve-google-token call failed: {exc}")
        logger.error(f"[appserver]    URL attempted: {url}")
        logger.error(f"[appserver]    Exception type: {type(exc).__name__}")
        return None, None, False
