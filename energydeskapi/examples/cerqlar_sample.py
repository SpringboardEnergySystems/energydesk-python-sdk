import logging
from energydeskapi.sdk.common_utils import init_api
import environ
from rauth import OAuth2Service
from energydeskapi.assets.assets_api import AssetsApi
import json
import requests
from energydeskapi.sdk.api_connection import ApiConnection, AuthorizationFailedException
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

trade_query={
  "quuery": {
    "filter": {},
    "page": {
      "pageSize": 100,
      "pageNumber": 0
    }
  }
}
def fetch_trades(base_url, token):
    trades_url=base_url + "/trading/v1/trades/search"
    print("Loading from " + trades_url)
    print(json.dumps(trade_query))
    headers = {"Authorization": "Bearer " + token,'accept': '*/*', 'Content-Type': 'application/json'}
    x = requests.post(trades_url, headers=headers, json=json.loads(json.dumps(trade_query)))

    print(json.dumps(x.json(), indent=2))

def cerqlar_token(client_id, client_secret, token_endpoint):
    payload={
      "client_id": client_id,
      "client_secret":client_secret,
      "audience": "cerqlar-backend",
      "grant_type": "client_credentials"
    }
    x = requests.post(token_endpoint, json=payload)
    if x.status_code==200:
        return x.json()['access_token']
    print(x.status_code)
    print(x.text)
    return None

if __name__ == '__main__':
    api_conn=init_api()
    env = environ.Env()
    client_id = env.str('CERQLAR_CLIENT_ID')
    client_secret = env.str('CERQLAR_CLIENT_SECRET')
    token_endpoint = env.str('CERQLAR_ACCESS_TOKEN_OBTAIN_URL')
    base_url = env.str('CERQLAR_BASE_URL')

    token=cerqlar_token(client_id, client_secret, token_endpoint)
    if token is not None:
        fetch_trades(base_url, token)

