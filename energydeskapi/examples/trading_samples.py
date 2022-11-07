import sys
import json

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.types.clearing_enum_types import ClearingReportTypeEnum
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def get_ticker_data(api_conn):
    df=LemsApi.get_traded_products(api_conn)
    print(df)
    ticker = df["ticker"].values[2]
    LemsApi.add_order(api_conn, ticker, 90, 2, "BUY")
    LemsApi.add_order(api_conn, ticker, 93, 2, "SELL")
if __name__ == '__main__':

    api_conn=init_api()

    get_ticker_data(api_conn)

