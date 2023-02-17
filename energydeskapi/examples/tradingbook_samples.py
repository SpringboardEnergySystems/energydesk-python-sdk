
import logging

import pandas as pd

from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def query_trading_books(api_conn):
    trading_books=TradingBooksApi.get_tradingbooks_compact(api_conn,{"page_size":100})
    print(trading_books['results'])
    df=pd.DataFrame(data=trading_books['results'])
    print(df)



def query_trading_books_by_type(api_conn):
    df=TradingBooksApi.get_tradingbooks_embedded(api_conn,[CommodityTypeEnum.POWER])
    print(df)
    #df=TradingBooksApi.get_tradingbooks_by_commodityfilter(api_conn,[CommodityTypeEnum.CURRENCY])
    #print(df)
if __name__ == '__main__':
    api_conn=init_api()
    query_trading_books(api_conn)
