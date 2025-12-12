import logging
from energydeskapi.sdk.common_utils import init_api
import environ
from rauth import OAuth2Service
from energydeskapi.assets.assets_api import AssetsApi
import json

from energydeskapi.sdk.api_connection import ApiConnection, AuthorizationFailedException
import base64
import requests
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
from rauth import OAuth2Service
def rauth_sample(client_id, client_secret, scope, token_endpoint, energydesk_base_url):
    service = OAuth2Service(client_id=client_id,client_secret = client_secret,access_token_url=token_endpoint)
    session = service.get_auth_session(data={'grant_type': 'client_credentials', "scope": scope}, decoder=json.loads)
    print(str(session.access_token))
    #earertoken = ApiConnection.validate_jwt_token(energydesk_base_url, str(session.access_token), "azuread-oauth2")
    api_conn=ApiConnection(energydesk_base_url,bearer_token=str(session.access_token))
    assets=AssetsApi.get_assets_embedded(api_conn)  # Accessing actual resource using the bearer token
    print(assets)


def get_access_token():
    env = environ.Env()
    client_id = env.str('OAUTH_CLIENT_ID')
    client_secret = env.str('OAUTH_CLIENT_SECRET')
    token_endpoint = env.str('OAUTHCHECK_ACCESS_TOKEN_OBTAIN_URL')
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
    if response.status_code != 200:
        raise AuthorizationFailedException(f"Failed to obtain access token from {token_endpoint}")
    token_json = response.json()
    print(json.dumps(token_json, indent=2))
    if "access_token_jwt" in token_json:
        return token_json["access_token_jwt"]
    else:
        return token_json["access_token"]


if __name__ == '__main__':

    api_conn=init_api()
    env = environ.Env()
    client_id = env.str('OAUTH_CLIENT_ID')
    client_secret = env.str('OAUTH_CLIENT_SECRET')
    scope = env.str('OAUTH_SCOPE')
    token_endpoint = env.str('OAUTHCHECK_ACCESS_TOKEN_OBTAIN_URL')
    edesk_base_url = env.str('ENERGYDESK_URL')
    rauth_sample(client_id, client_secret, scope, token_endpoint, edesk_base_url)
