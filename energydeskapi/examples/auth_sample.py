import environ
import json
import logging
import pandas as pd
import pendulum
import pytz
import requests

from energydeskapi.customers.users_api import UsersApi
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.sdk.common_utils import init_api

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


import base64

def authorize_user(token):
    """
    Validate token and get user information from Django OAuth backend.

    Args:
        token: The OAuth access token to validate

    Returns:
        dict: User information from the introspect endpoint, or None if validation fails
    """
    env = environ.Env()
    introspect_endpoint = env.str('OAUTH_INTROSPECT_ENDPOINT',
                                   default='https://hafslund-uat.energydesk.no/appserver/o/introspect/')
    client_id = env.str('OAUTH_CLIENT_ID')
    client_secret = env.str('OAUTH_CLIENT_SECRET')

    try:
        # Prepare the introspection request
        # Django OAuth Toolkit expects client credentials and the token
        data = {
            'token': token,
            'client_id': client_id,
            'client_secret': client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        # Call the introspect endpoint
        response = requests.post(introspect_endpoint, data=data, headers=headers)
        response.raise_for_status()

        user_info = response.json()

        # Check if token is active
        if user_info.get('active', False):
            logging.info(f"Token validated successfully for user: {user_info.get('username', 'unknown')}")
            logging.debug(f"User info: {json.dumps(user_info, indent=2)}")
            return user_info
        else:
            logging.warning("Token is not active")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error validating token: {e}")
        return None

def get_access_token():
    env = environ.Env()
    client_id = env.str('OAUTH_CLIENT_ID')
    client_secret = env.str('OAUTH_CLIENT_SECRET')
    token_endpoint = env.str('OAUTHCHECK_ACCESS_TOKEN_OBTAIN_URL')
    print("ID", client_id,"SECRET", client_secret)
    token_endpoint = env.str('OAUTHCHECK_ACCESS_TOKEN_OBTAIN_URL')
    concated_str=client_id + ":" + client_secret
    print(concated_str)

    data=(client_id + ":" + client_secret).replace(" ", "%20")
    encoded_bytes = base64.b64encode(data.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    body = "grant_type=client_credentials"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Basic " + encoded_str,
        "Cache-Control": "no-cache"
    }
    response = requests.request("POST", token_endpoint, data=body, headers=headers)

    token_json = response.json()
    print(json.dumps(token_json, indent=2))
    return token_json["access_token_jwt"] if "access_token_jwt" in token_json else token_json["access_token"] if "access_token" in token_json else None

def authorize_user_etrm(token):
    """
    Validate token and get user information from Django OAuth backend.

    Args:
        token: The OAuth access token to val
    """
    env = environ.Env()
    api_base_url = env.str('ENERGYDESK_URL')
    api_conn = ApiConnection(api_base_url)
    api_conn.set_token(tok, "Bearer")
    usrprofile = UsersApi.get_user_profile(api_conn)
    if usrprofile is not None:
        return (usrprofile['role_pk'],usrprofile['role'])
    else:
        print("No user profile found. Please check the API endpoint: ")

    return (None,None)

if __name__ == '__main__':
    api_conn = init_api()

    # Get an access token
    tok = get_access_token()

    if tok:
        # Validate the token and get user information
        user_info = authorize_user_etrm(tok)
        print(user_info)
        if user_info:
            pass
        #     print("\n✅ Token validated successfully!")
        #     print(f"User: {user_info.get('username', 'N/A')}")
        #     print(f"Active: {user_info.get('active', False)}")
        #     print(f"Scope: {user_info.get('scope', 'N/A')}")
        #     print(f"Client ID: {user_info.get('client_id', 'N/A')}")
        #     print(f"Token Type: {user_info.get('token_type', 'N/A')}")
        #     print(f"Expires at: {user_info.get('exp', 'N/A')}")

        else:
            print("\n❌ Token validation failed!")
    else:
        print("\n❌ Failed to obtain access token!")

    #print(df)