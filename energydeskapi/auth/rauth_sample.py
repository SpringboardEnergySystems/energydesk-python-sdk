import logging
from energydeskapi.sdk.common_utils import init_api
import environ
from rauth import OAuth2Service
import pandas as pd
import json
from http.client import HTTPSConnection
from urllib.parse import urljoin
import requests
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def rauth_sample(client_id, client_secret, scope, token_endpoint, elviz_proxy_url):
    service = OAuth2Service(client_id=client_id,client_secret = client_secret,access_token_url=token_endpoint)
    session = service.get_auth_session(data={'grant_type': 'client_credentials', "scope": scope}, decoder=json.loads)
    print(session.access_token)
    header={'Authorization':  "Bearer" + ' ' + str(session.access_token), 'Content-Type':'application/json'}
    r=session.post(elviz_proxy_url, data={}, headers=header)
    print(r, r.text)


if __name__ == '__main__':

    api_conn=init_api()
    env = environ.Env()
    elviz_proxy_url=env.str("ELVIZ_PROXY_SERVER_URL")
    client_id = env.str('OAUTH_CLIENT_ID')
    client_secret = env.str('OAUTH_CLIENT_SECRET')
    scope = env.str('OAUTH_SCOPE')
    token_endpoint = env.str('OAUTH_SERVER_TOKEN_ENDPOINT')
    #auth_endpoint = env.str('OAUTH_SERVER_AUTH_ENDPOINT')
    rauth_sample(client_id, client_secret, scope, token_endpoint, elviz_proxy_url)
