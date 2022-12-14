import logging
import pandas as pd
from energydeskapi.sdk.common_utils import parse_enum_type
from energydeskapi.sdk.money_utils import gen_json_money
from energydeskapi.types.market_enum_types import DeliveryTypeEnum
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.sdk.common_utils import check_fix_date2str
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

                 commodity_type=None,
                 instrument_type=None,
                 contract_status=None,
                 buy_or_sell=None,
                 counterpart=None,
                 market=None,
                 trader=None,
                 marketplace_product=None,
                 delivery_type=DeliveryTypeEnum.FINANCIAL.value,
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

        self.commodity_type=commodity_type
        self.instrument_type=instrument_type
        self.contract_status=contract_status
        self.buy_or_sell=buy_or_sell
        self.counterpart=counterpart
        self.market=market
        self.trader=trader
        self.marketplace_product=marketplace_product
        self.commodity_delivery_from = None
        self.commodity_delivery_until = None
        self.product_code=None
        self.otc_multi_delivery_periods=[]
        self.contract_tags=[]
        self.area="SYS"
        self.commodity_profile = "BASELOAD"
        self.spread = False
        self.otc = False
        self.delivery_type=delivery_type


    def add_contract_tag(self, tag):
        self.contract_tags.append(tag)

    def add_otc_delivery_period(self, delivery_from, delivery_until):
        if isinstance(delivery_from, str):
            self.otc_multi_delivery_periods.append({'period_from': delivery_from,
                                    'period_until': delivery_until,
                                    'price':gen_json_money(self.contract_price),
                                    'quantity': self.quantity})
        else:
            self.otc_multi_delivery_periods.append({'period_from':convert_datime_to_utcstr(delivery_from),
                                    'period_until':convert_datime_to_utcstr(delivery_until),
                                    'price':gen_json_money(self.contract_price),
                                    'quantity': self.quantity})
    def get_simple_dict(self):
        dict = {}
        dict['pk'] = self.pk
        prod = {}
        if self.instrument_type is not None: prod['instrument_type'] = self.instrument_type.value
        if self.commodity_type is not None: prod['commodity_type'] = self.commodity_type.value
        if self.delivery_type is not None: prod['delivery_type'] = self.delivery_type.value
        if self.commodity_delivery_from is not None: prod['delivery_from'] = check_fix_date2str(
            self.commodity_delivery_from)
        if self.commodity_delivery_until is not None: prod['delivery_until'] = check_fix_date2str(
            self.commodity_delivery_until)
        if self.market is not None: prod['market'] = self.market.value
        prod['area'] = self.area
        prod['commodity_profile'] = self.commodity_profile
        prod['spread'] = self.spread
        prod['otc'] = self.otc
        if self.product_code is not None:
            prod['product_code'] = self.product_code
        else:
            prod['otc'] = True
        dict['commodity'] = prod
        if self.external_contract_id is not None: dict['external_contract_id'] = self.external_contract_id
        if self.trading_book is not None: dict['trading_book'] = self.trading_book
        if self.trade_date is not None: dict['trade_date'] = self.trade_date
        dict['last_update_time'] = self.trade_datetime  # convert_datime_to_utcstr(datetime.now()),
        if self.trade_datetime is not None: dict['trade_time'] = self.trade_datetime
        if self.contract_price is not None: dict['contract_price'] = gen_json_money(self.contract_price)
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.trading_fee is not None: dict['trading_fee'] = gen_json_money(self.trading_fee)
        if self.clearing_fee is not None: dict['clearing_fee'] = gen_json_money(self.clearing_fee)
        # if self.contract_type is not None: dict['contract_type'] = self.contract_type
        if self.contract_status is not None: dict['contract_status'] = self.contract_status.value

        if self.buy_or_sell is not None: dict['buy_or_sell'] = self.buy_or_sell
        if self.counterpart is not None: dict['counterpart'] = self.counterpart
        if self.trader is not None: dict['trader'] = self.trader
        if self.marketplace_product is not None: dict[
            'marketplace_product'] = 0

        taglist = []
        for c in self.contract_tags:
            d = c.get_dict()
            print(d)
            taglist.append(d)
            # existing_tags=ContractsApi.get_contract_tags(api_conn, {"tagname": c})
            # if len(existing_tags)==0:  #Need to create new tag. Using tagname as description as default
            #     success, returned_data, status_code, error_msg=ContractsApi.upsert_contract_tag(api_conn, c)
            #     if success:
            #         taglist.append(returned_data)
            # else:
            #     taglist.append(existing_tags[0])
        dict['contract_tags'] = taglist
        if len(self.otc_multi_delivery_periods) > 0:
            dict["periods"] = self.otc_multi_delivery_periods

        return dict

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        prod = {}
        if self.instrument_type is not None: prod['instrument_type'] = MarketsApi.get_instrument_type_url(api_conn,self.instrument_type)
        if self.commodity_type is not None: prod['commodity_type'] = MarketsApi.get_commodity_type_url(api_conn, self.commodity_type)
        if self.delivery_type is not None: prod['delivery_type'] = MarketsApi.get_delivery_type_url(api_conn,
                                                                                                       self.delivery_type)
        if self.commodity_delivery_from is not None:prod['delivery_from'] = check_fix_date2str(self.commodity_delivery_from)
        if self.commodity_delivery_until is not None: prod['delivery_until'] = check_fix_date2str(self.commodity_delivery_until)
        if self.market is not None: prod['market'] = MarketsApi.get_market_url(api_conn, self.market)
        prod['area']=self.area
        prod['commodity_profile'] = self.commodity_profile
        prod['spread'] = self.spread
        prod['otc'] = self.otc
        if self.product_code is not None:
            prod['product_code'] = self.product_code
        else:
            prod['otc'] = True
        dict['commodity']=prod
        if self.external_contract_id is not None: dict['external_contract_id'] = self.external_contract_id
        if self.trading_book is not None: dict['trading_book'] = TradingBooksApi.get_tradingbook_url(api_conn,self.trading_book)
        if self.trade_date is not None: dict['trade_date'] = self.trade_date
        dict['last_update_time']=self.trade_datetime#convert_datime_to_utcstr(datetime.now()),
        if self.trade_datetime is not None: dict['trade_time'] = self.trade_datetime
        if self.contract_price is not None: dict['contract_price'] = gen_json_money(self.contract_price)
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.trading_fee is not None: dict['trading_fee'] = gen_json_money(self.trading_fee)
        if self.clearing_fee is not None: dict['clearing_fee'] = gen_json_money(self.clearing_fee)
        #if self.contract_type is not None: dict['contract_type'] = ContractsApi.get_contract_type_url(api_conn, self.contract_type)
        if self.contract_status is not None: dict['contract_status'] = ContractsApi.get_contract_status_url(api_conn,
                                                                                                            self.contract_status)

        if self.buy_or_sell is not None: dict['buy_or_sell'] = self.buy_or_sell
        if self.counterpart is not None: dict['counterpart'] = CustomersApi.get_company_url(api_conn, self.counterpart)
        if self.trader is not None: dict['trader'] = UsersApi.get_user_url(api_conn, self.trader)
        if self.marketplace_product is not None: dict['marketplace_product'] = api_conn.get_base_url() + "/api/markets/marketproducts/" + str(
                self.marketplace_product) + "/"

        taglist=[]
        for c in self.contract_tags:
            print(c)

            taglist.append(c)
            # existing_tags=ContractsApi.get_contract_tags(api_conn, {"tagname": c})
            # if len(existing_tags)==0:  #Need to create new tag. Using tagname as description as default
            #     success, returned_data, status_code, error_msg=ContractsApi.upsert_contract_tag(api_conn, c)
            #     if success:
            #         taglist.append(returned_data)
            # else:
            #     taglist.append(existing_tags[0])
        dict['contract_tags']=taglist
        if len(self.otc_multi_delivery_periods) > 0:
            dict["periods"] = self.otc_multi_delivery_periods

        return dict


class ContractTag:
    """ Class for contract tags

    """
    def __init__(self):
        self.pk = 0
        self.tagname = None
        self.description = None
        self.is_active = False
    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.tagname is not None: dict['tagname'] = self.tagname
        if self.description is not None:
            dict['description'] = self.description
        else:
            dict['tagname'] = self.description
        if self.is_active is not None: dict['is_active'] = self.is_active
        return dict


class ContractFilter:
    """ Class for contract filters

    """
    def __init__(self):
        self.pk=0
        self.user=None
        self.description=None
        self.filters=None
    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.user is not None: dict['user'] = self.user
        if self.description is not None: dict['description'] = self.description
        if self.filters is not None: dict['filters'] = self.filters
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
            #print(json.dumps(contract.get_dict(api_connection), indent=2))
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url('/api/portfoliomanager/contracts/' + str(contract.pk) + "/", contract.get_dict(api_connection))
        else:
            #print(json.dumps(contract.get_dict(api_connection), indent=2))
            success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/contracts/',contract.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

    @staticmethod
    def upsert_contract_tag(api_connection, tag):
        """Registers contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tag: contract tag to be registered
        :type tag: str, required
        """
        #logger.info("Registering contract tag")
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/portfoliomanager/contracttags/',tag.get_dict())
        return success, returned_data, status_code, error_msg

    @staticmethod
    def upsert_contract_from_dict(api_connection,
                        dict):
        """Registers contracts from dictionary

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param dict: dictionary
        :type dict: str, required
        """
        if dict['pk'] > 0:

            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/portfoliomanager/contracts/' + str(dict['pk']) + "/", dict)
        else:

            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/portfoliomanager/contracts/', dict)
        return success, returned_data, status_code, error_msg


    @staticmethod
    def upsert_contract_filters(api_connection, filter):
        """Registers/Updates contract filters

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param filter: contract filter object
        :type filter: str
        """
        logger.info("Upserting contract filter")

        if filter.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/portfoliomanager/contractfilters/' + str(filter.pk) + "/", filter.get_dict())
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/portfoliomanager/contractfilters/', filter.get_dict())
        return success, returned_data, status_code, error_msg

    @staticmethod
    def bulk_insert_contracts(api_connection,
                          contract_list):
        """Registers multiple contracts in a list. REST API does not return contracts, reducing bandwidth

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_list: contracts to be registered
        :type contracts: str, required
        """
        json_list=[]
        for c in contract_list:
            contract_dict=c.get_dict(api_connection)
            #print(json.dumps(contract_dict, indent=2))
            json_list.append(contract_dict)
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/contracts/bulkinsert/',json_list)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_contract_type_url(api_connection, contract_type_enum):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_type_enum: type of contract
        :type contract_type_enum: str, required
        """
        type_pk = contract_type_enum if isinstance(contract_type_enum, int) else contract_type_enum.value
        return api_connection.get_base_url() + '/api/portfoliomanager/contracttypes/' + str(type_pk) + "/"
    @staticmethod
    def get_contract_status_url(api_connection, contract_status_enum):
        """Fetches url for contract status from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        return api_connection.get_base_url() + '/api/portfoliomanager/contractstatuses/' + str(parse_enum_type(contract_status_enum)) + "/"

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
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/query-contracts/', query_payload)
        print(json_res)
        return None

    @staticmethod
    def query_contracts_df(api_connection, query_payload={"trading_book_key":0, "last_trades_count": 10}):
        """Queries contracts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param query_payload: personal key to a contract
        :type query_payload: str, required
        """
        logger.info("Fetching contracts")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/query-contracts-ext/', query_payload)
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_contract(api_connection, contract_pk):
        """Fetches contract from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_pk: payload used in query (default {"trading_book_key":0, "last_trades_count": 10})
        :type contract_pk: str
        """
        logger.info("Loading contract with pk " + str(contract_pk))
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/' + str(contract_pk) + "/")
        return json_res


    @staticmethod
    def get_contract_tag(api_connection, pk):
        """Fetches contract tags

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracttags/' + str(pk) + "/")
        return json_res

    @staticmethod
    def get_contract_tags(api_connection, parameters={}):
        """Fetches contract tags

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracttags/', parameters)
        return json_res

    @staticmethod
    def list_contracts(api_connection, parameters={}):
        """Lists contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: parameters to filter contracts
        :type parameters: str
        """
        logger.info("Listing contracts")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts', parameters)
        return json_res
    @staticmethod
    def list_contracts_embedded(api_connection, parameters={}):
        """Lists contracts with embedding

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: parameters to filter contracts
        :type parameters: str
        """
        logger.info("Listing contracts embedded")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/embedded/', parameters)
        return json_res
    @staticmethod
    def list_contracts_compact(api_connection, parameters={}):
        """Lists contracts with embedding

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: parameters to filter contracts
        :type parameters: str
        """
        logger.info("Listing contracts compact")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/compact/', parameters)
        return json_res
    @staticmethod
    def list_contracts_df(api_connection, parameters={}):
        """Lists contracts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: parameters to filter contracts
        :type parameters: str
        """
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/embedded/', parameters)
        print(json_res)
        #json_res=ContractsApi.list_contracts(api_connection, parameters)
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_commodity_type_url(api_connection, commodity_type_enum):
        """Fetches url for a commodity type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """

        return api_connection.get_base_url() + '/api/portfoliomanager/contractstatuses/' + str(parse_enum_type(commodity_type_enum)) + "/"

    @staticmethod
    def get_contract_url(api_connection, contract_pk):
        """Fetches url for contracts from pk

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
    def get_contract_filters(api_connection, parameters={}):
        """Fetches contract filters

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: parameters to filter contract filters
        :type parameters: str
        """
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contractfilters/', parameters)
        return json_res

    @staticmethod
    def get_contract_filter_by_key(api_connection, filter_pk):
        """Fetches contract filter from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param filter_pk: key to contract filter
        :type filter_pk: str, required
        """
        logger.info("Loading contract filter with pk " + str(filter_pk))
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contractfilters/' + str(filter_pk) + "/")
        return json_res

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
