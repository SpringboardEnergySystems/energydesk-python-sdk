import sys

import requests
import logging
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.sdk.common_utils import init_api
import pytz, environ
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_product_view(api_conn):
    filter={
        "trading_book":1
    }
    df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    print(df)
    filter={
        "trading_book":3
    }
    df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    print(df)
if __name__ == '__main__':
    api_conn=init_api()
    get_product_view(api_conn)
