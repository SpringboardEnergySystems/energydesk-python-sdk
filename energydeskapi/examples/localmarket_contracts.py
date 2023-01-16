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
import logging
from energydeskapi.sdk.common_utils import init_api
from datetime import datetime
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
from miscutils.timeconversion import current_timestamp_as_utcstr
from energydeskapi.sdk.money_utils import FormattedMoney
from uuid import uuid4
logger = logging.getLogger(__name__)

def generate_contract(prod_dict):
    for p in prod_dict:
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
        counterpart = "Volte AS"
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
        return

def get_historical_products(api_conn):
    res=LemsApi.get_all_local_products(api_conn)
    generate_contract(res)


import sys
if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    get_historical_products(api_conn)

