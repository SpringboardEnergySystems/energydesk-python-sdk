
import logging
import pandas as pd
from energydeskapi.bilateral.bilateral_api import BilateralApi, PricingConfiguration
from energydeskapi.profiles.profiles_api import ProfilesApi
from energydeskapi.profiles.profiles import GenericProfile
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
def query_historical_market_prices(api_conn):
    df=DerivativesApi.fetch_prices_in_period(api_conn,market_place= "Nasdaq OMX", market_name="Nordic Power", ticker=None, period_from="2022-12-15", period_until="2023-01-15")

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


import json
def get_commodity_profile(api_conn, ticker):
    res=ProductsApi.get_commodity_definitions(api_conn, {"product_code": ticker})
    cr=res['results']
    if len(cr)==1:
        print("Loaded commodity profile")
        dprof=GenericProfile.from_dict(cr[0]['commodity_profile'])
        print(dprof)
        delivery_from=cr[0]['delivery_from']
        delivery_until = cr[0]['delivery_until']
        success, returned_data, status_code, error_msg=ProfilesApi.convert_relativeprofile_to_yearlyfactors(
            api_conn, delivery_from, delivery_until,dprof
        )
        df=pd.DataFrame(data=json.loads(returned_data))
        df.index=df['datetime']
        df.index = pd.to_datetime(df.index)
        df=df.tz_convert("Europe/Oslo")
        print(df)

if __name__ == '__main__':
    #   pd.set_option('display.max_rows', None)
    api_conn=init_api()
    context = {}
    success, returned_data, status_code, error_msg=BilateralApi.load_profiled_volume(api_conn, "PROF3_NO1_5YR", 72000)

    context['price_area']=returned_data['area']
    context['delivery_from'] = returned_data['delivery_from']
    context['delivery_until'] = returned_data['delivery_until']
    context['df_yearly'] = returned_data['df_yearly'].to_json(orient='records',date_format='iso')
    context['df_monthly'] = returned_data['df_monthly'].to_json(orient='records',date_format='iso')





