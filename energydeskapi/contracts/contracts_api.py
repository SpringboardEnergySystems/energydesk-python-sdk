import requests
import json
import logging
import pandas as pd
from energydeskapi.sdk.money_utils import gen_json_money
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
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
                 maketplace,
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
        self.maketplace=maketplace
        self.trader=trader
        self.standard_product=standard_product
        self.deliveries=[]

    def add_delivery_period(self, delivery_from, delivery_until):
        self.deliveries.append({'delivery_from':convert_datime_to_utcstr(delivery_from),
                                'delivery_until':convert_datime_to_utcstr(delivery_until)})
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

            #trbook=TradingBooksApi.load_tradingbook_by_pk(api_connection, contract.trading_book)
            contract_record={
                   "external_contract_id": contract.external_contract_id,
                   "trading_book": api_connection.get_base_url() + "/api/portfoliomanager/tradingbook/" +
                                      str(contract.trading_book) + "/",
                   "trade_date": contract.trade_date,
                   "trade_time": contract.trade_datetime,
                   "last_update_time":convert_datime_to_utcstr(datetime.now()),
                   "contract_price": gen_json_money(contract.contract_price),
                    "quantity": contract.quantity,
                   "trading_fee": gen_json_money(contract.trading_fee),
                   "clearing_fee": gen_json_money(contract.clearing_fee),
                   "contract_type": api_connection.get_base_url() + "/api/portfoliomanager/contracttype/" +
                                      str(contract.contract_type.value) + "/",
                   "commodity_type": api_connection.get_base_url() + "/api/portfoliomanager/commoditytype/" +
                                      str(contract.commodity_type.value) + "/",
                   "instrument_type": api_connection.get_base_url() + "/api/portfoliomanager/instrumenttype/" +
                                      str(contract.instrument_type.value) + "/",
                   "contract_status": api_connection.get_base_url() + "/api/portfoliomanager/contractstatus/" +
                                      str(contract.contract_status.value) + "/",
                   "buy_or_sell": contract.buy_or_sell,
                   "counterpart": contract.counterpart,
                    "marketplace": contract.maketplace,
                    "trader": contract.trader}
            if contract.standard_product is not None:
                contract_record['standard_product']=api_connection.get_base_url() + "/api/markets/marketproduct/" + str(contract.standard_product) + "/"
            if len(contract.deliveries) > 0:
                contract_record["periods"]= contract.deliveries
            print(contract_record)
            json_records.append(contract_record)


        json_res=api_connection.exec_post_url('/api/portfoliomanager/register_contracts/',json_records)
        print(json_res)

    @staticmethod
    def load_tradingbook_by_pk(api_connection, pk):
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbook/')
        for r in json_res:
            if r['pk']==pk:
                return r
        return None

    @staticmethod
    def query_contracts(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        logger.info("Fetching contracts")
        json_res = api_connection.exec_post_url('/api/portfoliomanager/query_contracts/', query_payload)
        print(json_res)
        return None

    @staticmethod
    def query_contracts_df(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        logger.info("Fetching contracts")
        json_res = api_connection.exec_post_url('/api/portfoliomanager/query_contracts_ext/', query_payload)
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_contract_statuses(api_connection):
        logger.info("Fetching contract statues")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contractstatus/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_contract_types(api_connection):
        logger.info("Fetching contract types")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracttype/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_commodity_types(api_connection):
        logger.info("Fetching commodity types")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/commoditytype/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_instrument_types(api_connection):
        logger.info("Fetching instrument types")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/instrumenttype/')
        df = pd.DataFrame(data=json_res)
        return df