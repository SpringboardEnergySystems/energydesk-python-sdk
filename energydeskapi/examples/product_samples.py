import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.types.market_enum_types import MarketEnum
from os.path import join, dirname
from dotenv import load_dotenv
import pytz, environ
from dateutil import parser
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_market_products(api_conn):
    df=ProductsApi.get_products(api_conn, MarketEnum.NORDIC_POWER)
    #print(df)
    df=ProductsApi.get_products_verbose(api_conn, MarketEnum.NORDIC_POWER)
    print(df)




if __name__ == '__main__':
    logging.info("Loading environment")
    #dotenv_path = join(dirname(__file__), '.env')
    api_conn=init_api()
    get_market_products(api_conn)
