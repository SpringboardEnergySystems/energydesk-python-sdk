import sys

import requests
import logging
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.sdk.common_utils import init_api
import pytz, environ
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_trading_books(api_conn):
    df=TradingBooksApi.fetch_tradingbooks(api_conn)
    print(df)

if __name__ == '__main__':
    api_conn=init_api()
    query_trading_books(api_conn)
