import requests
import json
import logging
import pandas as pd
from energydeskapi.sdk.money_utils import gen_json_money
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from moneyed.l10n import format_money
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr
from datetime import datetime
logger = logging.getLogger(__name__)
#  Change
class Contract:
    """ Class for contracts

    """
    def __init__(self,
                 external_contract_id=None,
                 trading_book=None,
                 contract_price=None,
                 contract_qty=None,
                 trading_fee=None,
                 clearing_fee=None,
                 trade_date=None,
                 trade_datetime=None,
                 contract_type=None,
                 commodity_type=None,
                 instrument_type=None,
                 contract_status=None,
                 buy_or_sell=None,
                 counterpart=None,
                 marketplace=None,
                 trader=None,
                 standard_product=None
                 ):
        self.pk=0
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
        self.tags=[]

    def add_delivery_period(self, delivery_from, delivery_until):
        if isinstance(delivery_from, str):
            self.deliveries.append({'period_from': delivery_from,
                                    'period_until': delivery_until,
                                    'price':gen_json_money(self.contract_price),
                                    'quantity': self.quantity})
        else:
            self.deliveries.append({'period_from':convert_datime_to_utcstr(delivery_from),
                                    'period_until':convert_datime_to_utcstr(delivery_until),
                                    'price':gen_json_money(self.contract_price),
                                    'quantity': self.quantity})
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.external_contract_id is not None: dict['external_contract_id'] = self.external_contract_id
        if self.trading_book is not None: dict['trading_book'] = TradingBooksApi.get_tradingbook_url(api_conn,self.trading_book)
        if self.trade_date is not None: dict['trade_date'] = self.trade_date
        dict['last_update_time']=self.trade_datetime#convert_datime_to_utcstr(datetime.now()),
        if self.trade_datetime is not None: dict['trade_time'] = self.trade_datetime
        if self.contract_price is not None: dict['contract_price'] = gen_json_money(self.contract_price)
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.trading_fee is not None: dict['trading_fee'] = gen_json_money(self.trading_fee)
        if self.clearing_fee is not None: dict['clearing_fee'] = gen_json_money(self.clearing_fee)
        if self.contract_type is not None: dict['contract_type'] = ContractsApi.get_contract_type_url(api_conn, self.contract_type)
        if self.contract_status is not None: dict['contract_status'] = ContractsApi.get_contract_status_url(api_conn, self.contract_status)
        if self.instrument_type is not None: dict['instrument_type'] = MarketsApi.get_instrument_type_url(api_conn,
                                                                                                      self.instrument_type)
        if self.commodity_type is not None: dict['commodity_type'] = MarketsApi.get_commodity_type_url(api_conn,
                                                                                                      self.commodity_type)
        if self.buy_or_sell is not None: dict['buy_or_sell'] = self.buy_or_sell
        if self.counterpart is not None: dict['counterpart'] = CustomersApi.get_company_url(api_conn, self.counterpart)
        if self.marketplace is not None: dict['marketplace'] = CustomersApi.get_company_url(api_conn, self.marketplace)
        if self.trader is not None: dict['trader'] = UsersApi.get_user_url(api_conn, self.trader)
        if self.standard_product is not None: dict['standard_product'] = api_conn.get_base_url() + "/api/markets/marketproducts/" + str(
                self.standard_product) + "/"
        if len(self.deliveries) > 0:
            dict["periods"] = self.deliveries

        return dict
class ContractsApi:
    """Class for contracts in api

    """

    @staticmethod
    def upsert_contract(api_connection,
                          contract):
        """Registers contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contracts: contracts to be registered
        :type contracts: str, required
        """
        logger.info("Registering contract")
        #print(format_money(price, locale='en_DE'))
        #json_records=[]
        #json_records.append(contract.get_dict(api_connection))

        if contract.pk>0:
            json_res = api_connection.exec_patch_url('/api/portfoliomanager/contracts/' + str(contract.pk) + "/", contract.get_dict(api_connection))
        else:
            json_res = api_connection.exec_post_url('/api/portfoliomanager/contracts/',contract.get_dict(api_connection))
        return json_res

    @staticmethod
    def get_contract_type_url(api_connection, contract_type_enum):
        """Fetches contract type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_type_enum: type of contract
        :type contract_type_enum: str, required
        """
        return api_connection.get_base_url() + '/api/portfoliomanager/contracttypes/' + str(contract_type_enum.value) + "/"
    @staticmethod
    def get_contract_status_url(api_connection, contract_status_enum):
        """Fetches contract status from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        return api_connection.get_base_url() + '/api/portfoliomanager/contractstatuses/' + str(contract_status_enum.value) + "/"


    @staticmethod
    def load_tradingbook_by_pk(api_connection, pk):
        """Fetches tradingbooks from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key to a tradingbook
        :type pk: str, required
        """
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbooks/')
        for r in json_res:
            if r['pk']==pk:
                return r
        return None

    @staticmethod
    def query_contracts(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        """Queries contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param query_payload: payload used in query (default {"trading_book_key":0, "last_trades_count": 10})
        :type query_payload: str
        """
        logger.info("Fetching contracts")
        json_res = api_connection.exec_post_url('/api/portfoliomanager/query-contracts/', query_payload)
        print(json_res)
        return None

    @staticmethod
    def query_contracts_df(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        """Queries contracts and shows in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param query_payload: payload used in query (default {"trading_book_key":0, "last_trades_count": 10})
        :type query_payload: str
        """
        logger.info("Fetching contracts")
        json_res = api_connection.exec_post_url('/api/portfoliomanager/query-contracts-ext/', query_payload)
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_contract(api_connection, contract_pk):
        logger.info("Loading contract with pk " + str(contract_pk))
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/' + str(contract_pk) + "/")
        return json_res

    @staticmethod
    def list_contracts(api_connection, parameters={}):
        """Lists contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: description...
        :type parameters: str
        """
        logger.info("Listing contracts")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts', parameters)
        return json_res
    @staticmethod
    def list_contracts_df(api_connection, parameters={}):
        """Lists contracts and shows in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: description...
        :type parameters: str
        """
        json_res=ContractsApi.list_contracts(api_connection, parameters)
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_commodity_type_url(api_connection, commodity_type_enum):
        """Fetches commodity type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """
        return api_connection.get_base_url() + '/api/portfoliomanager/contractstatuses/' + str(commodity_type_enum.value) + "/"

    @staticmethod
    def get_contract_url(api_connection, contract_pk):
        """Fetches contract from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_pk: personal key to a contract
        :type contract_pk: str, required
        """
        return api_connection.get_base_url() + '/api/contracts/contract/' + str(contract_pk) + "/"

    @staticmethod
    def list_contract_statuses(api_connection):
        """Lists the statuses of contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching contract statuses")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contractstatuses/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_contract_types(api_connection):
        """Lists the types of contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching contract types")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracttypes/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_commodity_types(api_connection):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching commodity types")
        json_res = api_connection.exec_get_url('/api/markets/commoditytypes/')
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def list_instrument_types(api_connection):
        """Lists the types of instruments

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching instrument types")
        json_res = api_connection.exec_get_url('/api/markets/instrumenttypes/')
        df = pd.DataFrame(data=json_res)
        return df

    def fetch_standard_contract(api_connection, contract_pk):
        """Fetches standard contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_pk: personal key to a contract
        :type contract_pk: str, required
        """
        logger.info("Fetching full contract")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contract-details/' + str(contract_pk) + "/")

        return json_res

    def fetch_bilateral_contract(api_connection, contract_pk):
        """Fetches bilateral contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_pk: personal key to a contract
        :type contract_pk: str, required
        """
        logger.info("Fetching full bilat contract")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contract-details/' + str(contract_pk) + "/")
        return json_res
