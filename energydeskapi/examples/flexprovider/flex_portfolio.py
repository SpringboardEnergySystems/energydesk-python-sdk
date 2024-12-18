import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.flexibility.dso_api import DsoApi
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.sdk.profiles_utils import get_baseload_profile, get_default_availability_profile
from energydeskapi.types.flexibility_enum_types import AssetProfileTypeEnums
from energydeskapi.flexibility.flexibility_api import FlexibilityApi
from datetime import datetime
from energydeskapi.types.flexibility_enum_types import PortfolioStatusTypeEnums
from energydeskapi.flexibility.flexibility_portfolios_api import FlexibilityPortfolioApi,FlexPortfolioStatus, FlexPortfolio, FlexAsset
import pendulum
import json
import pandas as pd
import os
from energydeskapi.assetdata.baselines_utils import BaselinesModelsEnums, initialize_standard_algorithms, create_default_algo_parameters
import glob
import random
import sys
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def register_flex_portfolio(api_conn):
    assets = AssetsApi.get_assets(api_conn)
    lst=[]
    for idx, a in enumerate(assets['results']):
        id=a['asset_id']
        success, returned_data, status_code, error_msg = FlexibilityApi.upsert_flexible_asset(api_conn,
                                                                                              a['extern_asset_id'],
                                                                                              callback="https://127.0.0.1")
        fa=FlexAsset(id)
        lst.append(fa)
    fp=FlexPortfolio(0, "My Demo portfolio", "My demo", lst)
    print(fp.json)

    FlexibilityPortfolioApi.upsert_flexible_portfolio(api_conn, fp)

def load_flex_portfolios_details(api_conn):
    portos=FlexibilityPortfolioApi.get_flexible_portfolios_embedded(api_conn)
    print(portos)
def load_flex_portfolios(api_conn):


    portos=FlexibilityPortfolioApi.get_flexible_portfolios(api_conn)
    print(portos)
    for port in portos:
        port_url=FlexibilityPortfolioApi.get_flexible_portfolio_url(api_conn, port['pk'])
        status_url=FlexibilityPortfolioApi.get_flexible_portfolio_status_type_url(api_conn, PortfolioStatusTypeEnums.IDLE)
        fstat=FlexPortfolioStatus(0, port_url, status_url, timestamp_from=pendulum.now(tz="Europe/Oslo"), timestamp_until=None, tiggered_by_trade=None)
        FlexibilityPortfolioApi.upsert_flexible_portfolio_status(api_conn, fstat)
if __name__ == '__main__':
    api_conn=init_api()
    #register_flex_portfolio(api_conn)
    load_flex_portfolios(api_conn)
    load_flex_portfolios_details(api_conn)
    #load_available_flexibility(api_conn)
    #show_availability(api_conn)
    #show_dispatch_schedule(api_conn)
