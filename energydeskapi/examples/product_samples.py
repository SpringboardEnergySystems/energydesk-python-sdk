import pandas as pd
import logging
import json
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.types.market_enum_types import MarketEnum
from energydeskapi.marketdata.derivatives_api import DerivativesApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_market_products(api_conn):
    df=ProductsApi.get_products_df(api_conn, MarketEnum.NORDIC_POWER)
    print(df)

def get_prices(api_conn):
    param={'price_date__gte':"2024-03-20",'price_date__lt':"2024-03-21" }
    json_data=DerivativesApi.get_prices_flatlist(api_conn, param)

    print(json.dumps(json_data, indent=2))
def get_products(api_conn):
    param={}
    json_data=ProductsApi.get_market_products_objects(api_conn, param)


if __name__ == '__main__':
    logging.info("Loading environment")
    #pd.set_option('display.max_rows', None)
    #dotenv_path = join(dirname(__file__), '.env')
    api_conn=init_api()
    get_products(api_conn)
