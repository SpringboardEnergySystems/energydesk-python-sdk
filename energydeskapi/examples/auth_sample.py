import environ
import requests
import logging, pendulum
import os
from os.path import join, dirname
from matplotlib.pyplot import *
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.flexibility.flexibility_prequalify_api import FlexibilityPrequalifyApi
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.assetdata.assetdata_api import AssetDataApi
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
import pandas as pd
import json, pytz
from datetime import datetime
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
from energydeskapi.sdk.profiles_utils import get_default_availability_profile
from datetime import datetime, timedelta
from energydeskapi.assetdata.assetdata_api import AssetDataApi, TimeSeriesAdjustments, TimeSeriesAdjustment
from energydeskapi.flexibility.flexibility_prequalify_api import FlexPrequalBidTest
import json, ast
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum
from energydeskapi.graph.graph_utils import get_all_paths, calc_asset_ownerships
from django.http import JsonResponse, Http404, HttpResponseServerError, HttpResponseNotFound
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
from energydeskapi.assets.assets_api import AssetsApi, AssetType
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from urllib.parse import parse_qs
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


import base64

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
    return token_json["access_token_jwt"]
if __name__ == '__main__':
    api_conn = init_api()
    tok=get_access_token()
    api_conn.set_token(tok, "Bearer")
    assets=AssetsApi.get_assets(api_conn, {"description":"Unforseen_Consumption"})
    df = AssetDataApi.get_assetgroup_forecast_df(api_conn, [assets['results'][0]['pk']], PeriodResolutionEnum.MONTHLY)

    print(df)