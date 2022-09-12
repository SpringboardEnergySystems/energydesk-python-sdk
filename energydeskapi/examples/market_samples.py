import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.derivatives_api import DerivativesApi

from os.path import join, dirname
from dotenv import load_dotenv
import pytz, environ
from dateutil import parser
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_market_prices(api_conn):
    df=DerivativesApi.fetch_daily_prices(api_conn, "Nasdaq OMX", "Nordic Power", "NO1")
    print(df)



if __name__ == '__main__':
    api_conn=init_api()
    query_market_prices(api_conn)
