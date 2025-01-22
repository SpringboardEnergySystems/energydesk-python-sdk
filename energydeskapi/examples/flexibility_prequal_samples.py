import logging

import environ
import requests
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
import logging
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

def load_multiasset_data(apiconn, asset_pk_list=[], period_from:str="2024-10-01", period_until:str="2024-11-12", resolution= PeriodResolutionEnum.HOURLY.value):
    period_start = datetime.strptime(period_from, '%Y-%m-%d').replace(tzinfo=pytz.timezone("Europe/Oslo"))
    period_end = datetime.strptime(period_until, '%Y-%m-%d').replace(tzinfo=pytz.timezone("Europe/Oslo"))
    def load_asset_timeseries(asset_pk_list):
        params = {
            'id__in': [int(a) for a in asset_pk_list],
            'time_series_type__id': TimeSeriesTypesEnum.METERREADINGS.value,
            'resolution': resolution
        }
        print(params)
        jsdata = AssetDataApi.get_asset_timeseries(apiconn, params)
        if type(jsdata)==str:
            jsdata=json.loads(jsdata)
        df = pd.DataFrame(data=jsdata)
        if len(df)==0:
            return df
        df.index = df.timestamp
        df.index = pd.to_datetime(df.index)
        df = df.loc[(df.index >= period_start) & (df.index < period_end)]
        df = df.drop(columns=['date', 'timestamp'])
        return df

    df_metering = load_asset_timeseries(asset_pk_list)

    return df_metering

def get_access_token():
    init_api()
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
    token_json = response.json()
    return token_json["access_token_jwt"]

def register_prequal(api_conn):
    df_assets = AssetsApi.get_assets_df(api_conn,
                                            {'page_size': 1000, 'asset_category':AssetCategoryEnum.BATTERY.value})
    print(df_assets)
    pklist=[]
    for index, row in df_assets.iterrows():
        pklist.append(row['pk'])
    df_meterdata=load_multiasset_data(api_conn, pklist)

    df_metergroups = df_meterdata.pivot_table(index='timestamp', columns=['asset'], values='effect',
                                              aggfunc='mean')
    print(df_metergroups)
    df_tmp = make_empty_timeseries_df(str(df_metergroups.index.min())[:10], str(df_metergroups.index.max())[:10], "H")
    # df_tmp = pd.DataFrame(index=pd.date_range(str(df_metergroups.index.min())[:10], str(pendulum.tomorrow())[:10], freq='H'))
    import numpy as np
    df3 = pd.merge(df_tmp, df_metergroups, left_index=True, right_index=True, how='left')
    df3.replace(0, np.nan, inplace=True)
    df3 = df3.ffill()
    df3 = df3.bfill()
    df3['sum'] = df3.sum(axis=1)
    df3['sum']=df3['sum']/1000
    tseries=[]
    for index,row in df3.iterrows():
        record = {'timestamp': index.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
                  'value': row['sum']}
        tseries.append(record)

    timeseries_data = {
        'quantity_unit': "MW",
        'timeseries': tseries,
    }

    print(df3)
    print(df_meterdata)
    meters=df_meterdata['meter_id'].unique()
    extern_assets=[]
    for m in meters:
        a=AssetsApi.get_assets(api_conn, {'meter_id':m})
        extern_assets.append(a['results'][0]['asset_id'])

    profile=get_default_availability_profile(entry_value=0)
    profile['monthly_profile']['10']=1
    profile['monthly_profile']['11'] = 1
    profile['weekday_profile']['0'] = 1
    profile['weekday_profile']['1'] = 1
    profile['weekday_profile']['2'] = 1
    profile['weekday_profile']['3'] = 1
    profile['weekday_profile']['4'] = 1
    profile['weekday_profile']['4'] = 1
    profile['weekday_profile']['4'] = 1
    profile['weekday_profile']['4'] = 1

    profile['weekday_profile']['9'] = 1
    profile['weekday_profile']['10'] = 1
    profile['weekday_profile']['11'] = 1
    profile['weekday_profile']['12'] = 1
    profile['weekday_profile']['13'] = 1

    longflex_id="49803ce7-7c28-4409-83d7-b26800b67805"
    #asset_id_list = ['GUID1', 'GUID2', 'GUID3']
    success, returned_data, status_code, error_msg=FlexibilityPrequalifyApi.make_prequalification_request(api_conn,longflex_offer_id=longflex_id,
                                                                asset_id_list=extern_assets)
    if success:
        prequrl=FlexibilityPrequalifyApi.get_flex_prequalification_url(api_conn,returned_data['pk'])
        fbid = FlexPrequalBidTest(0,prequrl,profile,0.25, timeseries_data)
        FlexibilityPrequalifyApi.upsert_prequal_bidquality(api_conn, fbid)


def check_requests(api_conn):
    data=FlexibilityPrequalifyApi.get_prequal_bidquality_embedded(api_conn)
    for req in data['results']:
        print(req['pk']) # Key to which to update quality_measure
        print(req['prequalification'])
        print(req['offered_profile'])
        print(req['offered_capacity_mw'])
        print(req['quality_measure'])

def check_prequalification_requests(token=None):
    server_url="https://elvia.energydesk.no/appserver/api/flexibility/prequalification/bidqualitytest/embedded/"
    headers={'Authorization': 'Bearer ' + token}
    data = requests.get(server_url)
    for req in data.json()['results']:
        print("Key", req['pk']) # Key to which to update quality_measure
        print("Main qualification request",req['prequalification'])
        print("Profile",req['offered_profile'])
        #print("Meterdata",req['sample_portfolio_meterdata'])
        print("Offered capacity MW",req['offered_capacity_mw'])
        print("Quality measure", req['quality_measure'])

        # After checking the quality of the bid, report back the measured quality value
        #server_update_url = "https://elvia.energydesk.no/appserver/api/flexibility/prequalification/bidqualitytest/" + str(req['pk']) + "/"
        #data = requests.patch(server_update_url, {'quality_measure':3.14})
        #print(data.status_code)

if __name__ == '__main__':
    env = environ.Env()
    token=get_access_token()
    edesk_base_url = env.str('ENERGYDESK_URL')
    #api_conn=ApiConnection(edesk_base_url,bearer_token=str(token))
    #register_prequal(api_conn)
    #check_requests(api_conn)
    #print(token)
    check_prequalification_requests(token)
