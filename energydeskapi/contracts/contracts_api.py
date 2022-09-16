import requests
import json
import logging
import pandas as pd
from energydeskapi.sdk.money_utils import gen_json_money
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.marketdata.markets_api import MarketsApi
from moneyed.l10n import format_money
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr
from datetime import datetime
logger = logging.getLogger(__name__)
#  Change
class Contract:
    def __init__(self,
                 external_contract_id,
                 trading_book,
                 contract_price,
                 contract_qty,
                 trading_fee,
                 clearing_fee,
                 trade_date,
                 trade_datetime,
                 contract_type,
                 commodity_type,
                 instrument_type,
                 contract_status,
                 buy_or_sell,
                 counterpart,
                 marketplace,
                 trader,
                 standard_product=None
                 ):
        self.external_contract_id=external_contract_id
        self.trading_book=trading_book
        self.contract_price=contract_price
        self.quantity = contract_qty
        self.trading_fee=trading_fee
        self.clearing_fee=clearing_fee
        self.trade_date=trade_date
        self.trade_datetime=trade_datetime
        self.contract_type=contract_type
        self.commodity_type=commodity_type
        self.instrument_type=instrument_type
        self.contract_status=contract_status
        self.buy_or_sell=buy_or_sell
        self.counterpart=counterpart
        self.marketplace=marketplace
        self.trader=trader
        self.standard_product=standard_product
        self.deliveries=[]

    def add_delivery_period(self, delivery_from, delivery_until):
        self.deliveries.append({'delivery_from':convert_datime_to_utcstr(delivery_from),
                                'delivery_until':convert_datime_to_utcstr(delivery_until)})
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.external_contract_id is not None: dict['external_contract_id'] = self.external_contract_id
        if self.trading_book is not None: dict['trading_book'] = self.trading_book
        if self.trade_date is not None: dict['trade_date'] = self.trade_date
        if self.trade_datetime is not None: dict['trade_datetime'] = self.trade_datetime
        if self.contract_price is not None: dict['contract_price'] = self.contract_price
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.trading_fee is not None: dict['trading_fee'] = self.trading_fee
        if self.clearing_fee is not None: dict['clearing_fee'] = self.clearing_fee
        if self.contract_type is not None: dict['contract_type'] = ContractsApi.get_contract_type_url(api_conn, self.contract_type)
        if self.contract_status is not None: dict['contract_status'] = ContractsApi.get_contract_status_url(api_conn, self.contract_status)
        if self.instrument_type is not None: dict['instrument_type'] = MarketsApi.get_instrument_type_url(api_conn,
                                                                                                      self.instrument_type)
        if self.commodity_type is not None: dict['commodity_type'] = MarketsApi.get_commodity_type_url(api_conn,
                                                                                                      self.commodity_type)
        if self.buy_or_sell is not None: dict['buy_or_sell'] = self.buy_or_sell
        if self.counterpart is not None: dict['counterpart'] = self.counterpart
        if self.marketplace is not None: dict['marketplace'] = self.marketplace
        if self.trader is not None: dict['trader'] = self.trader
        if self.standard_product is not None: dict['standard_product'] = api_conn.get_base_url() + "/api/markets/marketproduct/" + str(
                self.standard_product) + "/"
        if len(self.deliveries) > 0:
            dict["periods"] = self.deliveries

        return dict
class ContractsApi:
    """Description...

      """

    @staticmethod
    def register_contract(api_connection,
                          contracts):
        logger.info("Registering contract")
        #print(format_money(price, locale='en_DE'))
        json_records=[]
        for contract in contracts:
            json_records.append(contract.get_dict(api_connection))
        json_res=api_connection.exec_post_url('/api/portfoliomanager/register-contracts/',json_records)


    @staticmethod
    def get_contract_type_url(api_connection, contract_type_enum):
        return api_connection.get_base_url() + '/api/portfoliomanager/contracttypes/' + str(contract_type_enum.value) + "/"
    @staticmethod
    def get_contract_status_url(api_connection, contract_status_enum):
        return api_connection.get_base_url() + '/api/portfoliomanager/contractstatuses/' + str(contract_status_enum.value) + "/"


    @staticmethod
    def load_tradingbook_by_pk(api_connection, pk):
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbooks/')
        for r in json_res:
            if r['pk']==pk:
                return r
        return None

    @staticmethod
    def query_contracts(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        logger.info("Fetching contracts")
        json_res = api_connection.exec_post_url('/api/portfoliomanager/query-contracts/', query_payload)
        print(json_res)
        return None

    @staticmethod
    def query_contracts_df(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        logger.info("Fetching contracts")
        json_res = api_connection.exec_post_url('/api/portfoliomanager/query-contracts-ext/', query_payload)
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_commodity_type_url(api_connection, commodity_type_enum):
        return api_connection.get_base_url() + '/api/portfoliomanager/contractstatuses/' + str(commodity_type_enum.value) + "/"

    @staticmethod
    def get_contract_type_url(api_connection, contract_type_enum):
        return api_connection.get_base_url() + '/api/portfoliomanager/contracttypes/' + str(contract_type_enum.value) + "/"


    @staticmethod
    def get_contract_url(api_connection, contract_pk):
        return api_connection.get_base_url() + '/api/contracts/contract/' + str(contract_pk) + "/"

    @staticmethod
    def list_contract_statuses(api_connection):
        logger.info("Fetching contract statues")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contractstatuses/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_contract_types(api_connection):
        logger.info("Fetching contract types")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracttypes/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_commodity_types(api_connection):
        logger.info("Fetching commodity types")
        json_res = api_connection.exec_get_url('/api/markets/commoditytypes/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_instrument_types(api_connection):
        logger.info("Fetching instrument types")
        json_res = api_connection.exec_get_url('/api/markets/instrumenttypes/')
        df = pd.DataFrame(data=json_res)
        return df