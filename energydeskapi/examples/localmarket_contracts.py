import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi, LocalProduct
import pandas as pd
import pytz
from energydeskapi.types.market_enum_types import DeliveryTypeEnum
from os.path import join, dirname
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum
from datetime import datetime
from energydeskapi.profiles.profiles_api import ProfilesApi, VolumeProfile
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
import logging
from energydeskapi.lems.lems_api import LemsApi, CustomProfile
from energydeskapi.sdk.common_utils import init_api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.types.contract_enum_types import ContractStatusEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, DeliveryTypeEnum,MarketEnum, InstrumentTypeEnum
from moneyed import NOK
from dateutil.relativedelta import relativedelta
from miscutils.timeconversion import current_timestamp_as_utcstr
from energydeskapi.sdk.money_utils import FormattedMoney
from uuid import uuid4
logger = logging.getLogger(__name__)

def generate_contract(prod_dict):

    for p in prod_dict:
        for comp in ['Entelios AS', 'Volte AS']:
            print(p)
            print(p['ticker'])

            deal_id=str(uuid4())
            trade_id = str(uuid4())
            loc_ticker = p['ticker']

            delivery_from= p['commodity_definition']['delivery_from']
            delivery_until = p['commodity_definition']['delivery_until']

            price = 1200
            buy_sell = "SELL"
            quantity = 4
            counterpart = comp
            create_at = current_timestamp_as_utcstr()#p['traded_until']
            tb=-1
            tbs=TradingBooksApi.get_tradingbooks(api_conn, {'page_size':100, 'contract_types':1})
            for tb in tbs['results']:
                if tb['description']=='Bilateral Fixed Price':
                    tb=tb['pk']


            comdef=MarketsApi.get_commodity(api_conn, {'product_code':loc_ticker})
            delivery_type = DeliveryTypeEnum.PHYSICAL
            commodity_type = CommodityTypeEnum.POWER
            contract_status = ContractStatusEnum.REGISTERED
            instrument_type = InstrumentTypeEnum.FWD
            counterpart_dict=CustomersApi.get_companies(api_conn,  {'name__icontains':counterpart})
            if len(counterpart_dict['results'])==0:
                continue

            counterpart_pk=counterpart_dict['results'][0]['pk']
            prof = UsersApi.get_user_profile(api_conn)
            tader_pk = prof['pk']
            c=Contract(trade_id, tb,
                        FormattedMoney(price, NOK),round(quantity, 1),
                        FormattedMoney(0, NOK),
                        FormattedMoney(0, NOK),
                       create_at[0:10],create_at,
                       commodity_type,
                       instrument_type,
                       contract_status,
                       buy_sell,
                       counterpart_pk,
                       MarketEnum.NORDIC_POWER,
                       tader_pk)

            c.contract_status = ContractStatusEnum.CONFIRMED
            c.commodity_delivery_from = delivery_from
            c.commodity_delivery_until =delivery_until
            c.product_code = loc_ticker
            c.area=loc_ticker[3:6]
            c.commodity_profile="BASELOAD"
            print(c.get_dict(api_conn))
            ContractsApi.upsert_contract(api_conn,c)


def get_historical_products(api_conn):
    res=LemsApi.get_all_local_products(api_conn)
    generate_contract(res)

def add_custom_profile_order(api_conn, profile, price, quantity):
    thismonth = date.today().replace(day=1)
    expiry = date.today() + relativedelta(days=3)
    dt_from = thismonth + relativedelta(month=3)
    dt_until = thismonth + relativedelta(month=12)
    concrete_profile_inc_period = CustomProfile()
    concrete_profile_inc_period.volume_profile={'monthly_profile':profile['monthly_profile'],
                    'weekday_profile':profile['weekday_profile'],
                    'daily_profile':profile['daily_profile'],
                   }
    concrete_profile_inc_period.price_area="NO5"
    concrete_profile_inc_period.delivery_from=dt_from.strftime("%Y-%m-%d")
    concrete_profile_inc_period.delivery_until = dt_until.strftime("%Y-%m-%d")
    success, json_res, status_code, error_msg=LemsApi.upsert_custom_profile(api_conn, concrete_profile_inc_period)
    if success:
        print("Got ticker to use in order entry", json_res['ticker'])
        LemsApi.add_order(api_conn, json_res['ticker'], price, "NOK", quantity, "BUY", "NORMAL", expiry.strftime("%Y-%m-%d"), "ACTIVE")

def create_profile(api_conn):
    months=get_baseload_months()
    months['June'] = 0.7
    months['July']=0.4
    months['August'] = 0.4
    weekdays=get_baseload_weekdays()
    hours=get_baseload_dailyhours()
    v=VolumeProfile()
    v.profile={
        'monthly_profile': months,
        'weekday_profile': weekdays,
        'daily_profile': hours
    }
    v.description="customprofile3"
    jsres = ProfilesApi.upsert_volume_profile(api_conn, v)
    print(jsres)

def manage_myown_profiles(api_conn):
    create_profile(api_conn)

    jsdata = ProfilesApi.get_volume_profiles(api_conn)
    print(jsdata)

    jsdata=ProfilesApi.get_volume_profiles(api_conn,{'description':"customprofile3"})
    if len(jsdata['results'])>0:
        selected_profile=jsdata['results'][0]['profile']
        print(selected_profile)
        add_custom_profile_order(api_conn, selected_profile, 999, 5)

from energydeskapi.types.market_enum_types import MarketEnum
import sys
if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)

    api_conn=init_api()
    manage_myown_profiles(api_conn)

