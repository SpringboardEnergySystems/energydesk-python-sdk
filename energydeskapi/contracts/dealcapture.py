import logging
import copy
from random import randrange
import random
from dateutil import parser
import json
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.types.contract_enum_types import ContractStatusEnum, ContractTypeEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, DeliveryTypeEnum,MarketEnum, InstrumentTypeEnum
from os.path import join, dirname
from moneyed import EUR, NOK
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr, convert_datime_to_locstr
from dotenv import load_dotenv
from energydeskapi.sdk.money_utils import FormattedMoney

def bilateral_dealcapture(api_conn):

    trades = LemsApi.get_own_trades(api_conn)
    for t in trades:
        print(t)
        deal_id=t['deal_id']
        trade_id = t['trade_id']
        loc_ticker = t['ticker']
        price = t['price']
        buy_sell = t['side']
        quantity = t['quantity']
        counterpart = t['counterpart']
        create_at = t['create_at']
        tbs=TradingBooksApi.get_tradingbooks(api_conn, {'page_size':100, 'contract_types':1})
        for tb in tbs['results']:
            print(tb)
        tb=30

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
                    FormattedMoney(price, NOK),quantity,
                    FormattedMoney(0, NOK),
                    FormattedMoney(0, NOK),
                   create_at[0:10],create_at, ContractTypeEnum.PHYSICAL,
                   commodity_type,
                   instrument_type,
                   contract_status,
                   buy_sell,
                   counterpart_pk,
                   MarketEnum.NORDIC_POWER,
                   tader_pk)
        print(c.get_dict(api_conn))
        c.contract_status = ContractStatusEnum.CONFIRMED
        #c.commodity_delivery_from = parser.isoparse(selected_poduct['delivery_from'].iloc[0])
        #c.commodity_delivery_until = parser.isoparse(selected_poduct['delivery_until'].iloc[0])
        c.product_code = loc_ticker
        c.commodity_profile="BASELOAD"
        ContractsApi.upsert_contract(api_conn,c)