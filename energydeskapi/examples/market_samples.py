
import logging
import pandas as pd
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.marketdata.spotprices_api import SpotPricesApi
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.types.market_enum_types import MarketEnum, CommodityTypeEnum, InstrumentTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_market_prices(api_conn):
    df=DerivativesApi.fetch_daily_prices(api_conn, "Nasdaq OMX", "Nordic Power", "ALL")

    print(df)

def query_market_types(api_conn):

    url=MarketsApi.get_market_url(api_conn, MarketEnum.CURRENCY_MARKET)
    print(MarketEnum.CURRENCY_MARKET, url)
    url=MarketsApi.get_commodity_type_url(api_conn, CommodityTypeEnum.CURRENCY)
    print(CommodityTypeEnum.CURRENCY, url)
    url=MarketsApi.get_instrument_type_url(api_conn, InstrumentTypeEnum.FWD)
    print(InstrumentTypeEnum.FWD, url)
def get_spot_prices(api_conn):
    df=SpotPricesApi.get_spot_prices_df(api_conn)
    print(df)
def manage_market_products(api_conn, ticker):
    res=ProductsApi.get_market_products(api_conn, {'market_ticker':ticker})
    print("Lookup ", ticker, " got ", res['results'])
    if len(res['results'])==0:
        print("Need to create product")
        res=ProductsApi.generate_market_product_from_ticker(api_conn,"Nasdaq OMX", ticker)
        print(res)

def get_market_types(api_conn):

    res=MarketsApi.get_instrument_types(api_conn)
    print(res)
    res=MarketsApi.get_commodity_types(api_conn)
    print(res)
if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    api_conn=init_api()
    query_market_prices(api_conn)
