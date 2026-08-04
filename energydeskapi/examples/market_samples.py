from energydeskapi.types.market_enum_types import MarketEnum, MarketPlaceEnum
import logging
import pandas as pd
import environ
from energydeskapi.bilateral.bilateral_api import BilateralApi
from energydeskapi.profiles.profiles_api import ProfilesApi
from energydeskapi.profiles.profiles import GenericProfile
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.market_enum_types import MarketEnum
from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.marketdata.spotprices_api import SpotPricesApi
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.moneymarkets.moneymarkets_api import MoneyMarketsApi
from finance.options.opcalc import asian_76,american,american_76,black_76,black_scholes,merton,garman_kohlhagen,kirks_76
from finance.options.impl.helpers import assert_close
from datetime import datetime
import pendulum
from energydeskapi.types.market_enum_types import MarketEnum, CommodityTypeEnum, InstrumentTypeEnum
from energydeskapi.types.market_enum_types import BlockSizeEnum,StructureTypeEnum,CommodityTypeEnum, DeliveryTypeEnum, InstrumentTypeEnum, MarketPlaceEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def query_fx(api_conn):
    par={"days_back":1000}
    data=MoneyMarketsApi.get_fxspot(api_conn, par)
    print(data)
def query_market_prices(api_conn):
    today = pendulum.today('Europe/Oslo')
    pastday = today.add(days=-20)
    yesterday = today.add(days=-1)
    #yesterday = pendulum.timezone("Europe/Paris").convert(yesterday)
    params={"price_date__gte": str(pastday),"price_date__lt": str(yesterday), 'page_size':1000}

    #jd=DerivativesApi.get_prices_flatlist(api_conn, params)
    jd=DerivativesApi.fetch_daily_prices(api_conn,MarketPlaceEnum.NASDAQ_OMX.name,MarketEnum.NORDIC_POWER.name,"ALL")
    #df=DerivativesApi.fetch_prices_in_period(api_conn,market_place= MarketPlaceEnum.NASDAQ_OMX.name, market_name=MarketEnum.NORDIC_POWER.name, ticker=None, period_from="2022-12-15", period_until="2023-01-15")
    df=pd.DataFrame(data=json.loads(jd))
    print(df)

def query_product_prices(api_conn, products=['FEUA042026P086','FEUA042026']):
    today = pendulum.today('Europe/Oslo')
    period_from = today.add(days=-5)
    period_until = today
    params={ 'page_size':50}
    params['price_date__gte'] = str(period_from)[:10]
    params['price_date__lt'] = str(period_until)[:10]
    params['product__commodity_definition__instrument_type__code__in'] = ["FUT"]
    params['product__market_place__name__in'] = ["ICE"]
    data=DerivativesApi.get_product_prices(api_conn, params)
    #print(json.dumps(data['results'], indent=2))

def query_market_prices_embedded(api_conn):
    yesterday = pendulum.yesterday('Europe/Oslo')
    today = pendulum.today('Europe/Oslo')
    params={"price_date": str(yesterday),"price_date__lt": str(today), 'page_size':1000}
    params={'page_size':1000, 'area_filter__in':['SYS',"NO1"]}
    jd=DerivativesApi.get_prices(api_conn, params)
    print(jd)

def calculate_option_params(api_conn):
    today = pendulum.today('Europe/Oslo')
    period_from = today.add(days=0)
    params={ 'page_size':5000}
    params['price_date'] = str(period_from)[:10]
    params['product__market_place__name'] = "ICE"
    data=DerivativesApi.get_prices_embedded_json(api_conn, params)
    #print(json.dumps(data['results'], indent=2))
    for prod in data['results']:
        ticker =prod['product']['market_ticker']
        instr_code = prod['product']['commodity_definition']['instrument_type']['code']
        #print(ticker, instr_code)
        if instr_code=="EUROPT":
            pass
            #print(ticker, instr_code)
            #bs = black_scholes('c', 3000, 5000, 1, 0.03, 0.4)
            #print(bs)
        elif instr_code=="FUT":
            print(ticker, instr_code)
            #bs = black_scholes('c', 3000, 5000, 1, 0.03, 0.4)
            #print(bs)
def query_market_types(api_conn):

    url=MarketsApi.get_market_url(api_conn, MarketEnum.CURRENCY_MARKET)
    print(MarketEnum.CURRENCY_MARKET, url)
    url=MarketsApi.get_commodity_type_url(api_conn, CommodityTypeEnum.CURRENCY)
    print(CommodityTypeEnum.CURRENCY, url)
    url=MarketsApi.get_instrument_type_url(api_conn, InstrumentTypeEnum.FWD)
    print(InstrumentTypeEnum.FWD, url)

def get_spot_prices(api_conn):
    today = pendulum.today('Europe/Oslo')
    period_from = pendulum.parse("2026-03-01", tz="Europe/Oslo")
    period_until = pendulum.parse("2026-04-01", tz="Europe/Oslo")
    #params={"period_from": str(period_from),"period_until": str(today), 'currency_code':'NOK', 'resolution':'h','area':'NO1','market':'NORDIC_POWER','page_size':1000}
    parameters = {
        'period_from': str(pendulum.parse(str(period_from), tz="Europe/Oslo")) if period_from else None,
        'period_until': str(pendulum.parse(str(period_until), tz="Europe/Oslo")) if period_from else None,
        'resolution': "D",
        'currency_code': "NOK",
        'market': "NORDIC_POWER",
        'area': "NO1"
    }
    print(parameters)
    df=SpotPricesApi.get_spot_prices_df(api_conn, parameters)
    if df is not None:
        df_no1=df['SYS']
        pd.set_option('display.max_rows', None)
        print(df_no1)
        # Print average price for each day
        print("Average price for each day:")
        print(df_no1.mean())





def manage_market_products(api_conn, ticker):
    res=ProductsApi.get_market_products(api_conn, {'market_ticker':ticker})
    print("Lookup ", ticker, " got ", res['results'])
    if len(res['results'])==0:
        print("Need to create product")

        res=ProductsApi.generate_market_product_from_ticker(api_conn,MarketPlaceEnum.NASDAQ_OMX, ticker)
        print(res)


def market_products(api_conn):
    params={'page_size':500}
    #params['commodity_definition__instrument_type__code']=InstrumentTypeEnum.EUROPT.name
    params['market_ticker']= "IEUA112026"
    res=ProductsApi.get_market_products_embedded(api_conn, params)

    #pd.set_option('display.max_rows', None)
    #print(df)
    #print(df[['product_code','generic_product_code','price_basis_code']])
    print(json.dumps(res['results'], indent=2))


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
from energydeskapi.sdk.api_connection import ApiConnection
def compare_spot_prices(api_conn):
    def load_spot(conn):
        today = pendulum.today('Europe/Oslo')
        period_from = pendulum.parse("2025-12-31", tz="UTC")
        params={"period_from": str(period_from),"period_until": str(today), 'currency_code':'NOK', 'resolution':'h','area':'NO1','market':'NORDIC_POWER','page_size':1000}
        df=SpotPricesApi.get_spot_prices_df(conn, params)
        df_no1=df['NO1']
        pd.set_option('display.max_rows', None)
        print(df_no1)

    load_spot(api_conn)
    env = environ.Env()
    url2= env.str('ENERGYDESK_URL2')
    token2 = env.str('ENERGYDESK_TOKEN2')

    api_conn2=ApiConnection(url2)
    api_conn2.set_token(token2, "Token")
    load_spot(api_conn2)


if __name__ == '__main__':
    #   pd.set_option('display.max_rows', None)
    api_conn=init_api()

    context = {}
    #market_products(api_conn)
    query_product_prices(api_conn)
    #get_spot_prices(api_conn)
    #df=ProductsApi.get_market_products_df(api_conn, {'page_size':500, 'commodity_definition__instrument':'2025-01-01'})
    #print(df)
    #get_spot_prices(api_conn)
    #query_product_prices(api_conn, ['ENOFUTBLYR-26','ENOFUTBLYR-27'])
    ##success, returned_data, status_code, error_msg=BilateralApi.load_profiled_volume(api_conn, "PROF3_NO1_5YR", 72000)
    #context['price_area']=returned_data['area']
    #context['delivery_from'] = returned_data['delivery_from']
    #context['delivery_until'] = returned_data['delivery_until']
    #context['df_yearly'] = returned_data['df_yearly'].to_json(orient='records',date_format='iso')
    #context['df_monthly'] = returned_data['df_monthly'].to_json(orient='records',date_format='iso')





