import logging
from energydeskapi.sdk.common_utils import init_api
import environ
from rauth import OAuth2Service
from energydeskapi.assets.assets_api import AssetsApi
import json

from energydeskapi.sdk.api_connection import ApiConnection, AuthorizationFailedException
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def rauth_sample(client_id, client_secret, scope, token_endpoint):
    service = OAuth2Service(client_id=client_id,client_secret = client_secret,access_token_url=token_endpoint)
    session = service.get_auth_session(data={'grant_type': 'client_credentials', "scope": scope}, decoder=json.loads)
    bearertoken = ApiConnection.validate_jwt_token("http://127.0.0.1:8001", str(session.access_token), "azuread-oauth2")
    api_conn=ApiConnection("http://127.0.0.1:8001",bearer_token=bearertoken)
    ass=AssetsApi.get_assets_embedded(api_conn)
    print(ass)



if __name__ == '__main__':

    api_conn=init_api()
    env = environ.Env()
    client_id = env.str('OAUTH_CLIENT_ID')
    client_secret = env.str('OAUTH_CLIENT_SECRET')
    scope = env.str('OAUTH_SCOPE')
    token_endpoint = env.str('OAUTHCHECK_ACCESS_TOKEN_OBTAIN_URL')
    #auth_endpoint = env.str('OAUTH_SERVER_AUTH_ENDPOINT')
    rauth_sample(client_id, client_secret, scope, token_endpoint)
