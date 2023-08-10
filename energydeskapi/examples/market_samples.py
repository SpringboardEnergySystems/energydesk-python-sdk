
import logging
import pandas as pd
from energydeskapi.bilateral.bilateral_api import BilateralApi
from energydeskapi.profiles.profiles_api import ProfilesApi
from energydeskapi.profiles.profiles import GenericProfile
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.marketdata.spotprices_api import SpotPricesApi
from energydeskapi.marketdata.products_api import ProductsApi
from datetime import datetime
import pendulum
from energydeskapi.types.market_enum_types import MarketEnum, CommodityTypeEnum, InstrumentTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_market_prices(api_conn):
    today = pendulum.today('Europe/Oslo')
    pastday = today.add(days=-20)
    yesterday = today.add(days=-1)
    #yesterday = pendulum.timezone("Europe/Paris").convert(yesterday)
    params={"price_date__gte": str(pastday),"price_date__lt": str(today), 'page_size':1000}
    #params={'page_size':1000, 'area_filter__in':['SYS',"NO1"]}
    print(params)
    #params={}
    jd=DerivativesApi.get_prices_flatlist(api_conn, params)
    #df=DerivativesApi.fetch_prices_in_period(api_conn,market_place= "Nasdaq OMX", market_name="Nordic Power", ticker=None, period_from="2022-12-15", period_until="2023-01-15")
    df=pd.DataFrame(data=eval(jd['results']))
    print(df)

def query_market_prices_embedded(api_conn):
    yesterday = pendulum.yesterday('Europe/Oslo')
    today = pendulum.today('Europe/Oslo')
    params={"price_date__gte": str(yesterday),"price_date__lt": str(today), 'page_size':1000}
    params={'page_size':1000, 'area_filter__in':['SYS',"NO1"]}
    jd=DerivativesApi.get_prices_embedded_json(api_conn, params)
    print(jd)

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

    df=query_market_prices(api_conn)
    print(df)
    #success, returned_data, status_code, error_msg=BilateralApi.load_profiled_volume(api_conn, "PROF3_NO1_5YR", 72000)
    #context['price_area']=returned_data['area']
    #context['delivery_from'] = returned_data['delivery_from']
    #context['delivery_until'] = returned_data['delivery_until']
    #context['df_yearly'] = returned_data['df_yearly'].to_json(orient='records',date_format='iso')
    #context['df_monthly'] = returned_data['df_monthly'].to_json(orient='records',date_format='iso')





