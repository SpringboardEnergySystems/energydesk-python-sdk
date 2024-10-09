import logging
import pandas as pd
from energydeskapi.sdk.common_utils import parse_enum_type,convert_loc_datetime_to_utcstr
from energydeskapi.contracts.contract_class import Contract
import json

logger = logging.getLogger(__name__)


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

    @staticmethod
    def from_dict(d):
        ct=ContractTag()
        ct.pk=d['pk']
        ct.tagname = d['tagname']
        ct.description = d['description']
        ct.is_active = d['is_active']
        return ct

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
                          contract: Contract):
        """Registers contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contracts: contracts to be registered
        :type contracts: str, required
        """
        logger.info("Registering contract")
        if type(contract) is dict:
            key=contract['pk']
            contract_dict=contract
        else:
            key=contract.pk
            contract_dict=contract.get_dict(api_connection)
        print("Key", key, contract_dict)
        if key>0:

            #print(json.dumps(contract.get_dict(api_connection), indent=2))
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url('/api/portfoliomanager/contracts/' + str(key) + "/", contract_dict)
        else:
            print(contract_dict)
            #print(json.dumps(contract.get_dict(api_connection), indent=2))
            success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/contracts/',contract_dict)
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
                          contract_list: list[Contract]):
        """Registers multiple contracts in a list. REST API does not return contracts, reducing bandwidth

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_list: contracts to be registered
        :type contracts: str, required
        """
        json_list=[]
        for c in contract_list:
            contract_dict=c.get_dict(api_connection)
            logger.debug(json.dumps(contract_dict, indent=2))
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
    def get_quantity_type_url(api_connection, quantity_type_enum):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param quantity_type_enum: type of contract
        :type quantity_type_enum: str, required
        """
        type_pk = quantity_type_enum if isinstance(quantity_type_enum, int) else quantity_type_enum.value
        return api_connection.get_base_url() + '/api/portfoliomanager/quantitytypes/' + str(type_pk) + "/"

    @staticmethod
    def get_quantity_unit_url(api_connection, quantity_unit_enum):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param quantity_unit_enum: type of contract
        :type quantity_unit_enum: str, required
        """
        type_pk = quantity_unit_enum if isinstance(quantity_unit_enum, int) else quantity_unit_enum.value
        return api_connection.get_base_url() + '/api/portfoliomanager/quantityunits/' + str(type_pk) + "/"


    @staticmethod
    def get_contract_types(api_connection, parameters={}):
        """Fetches all quantity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/portfoliomanager/contracttypes/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_quantity_units(api_connection, parameters={}):
        """Fetches all quantity units

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/portfoliomanager/quantityunits/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_quantity_types(api_connection, parameters={}):
        """Fetches all quantity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/portfoliomanager/quantitytypes/', parameters)
        if json_res is None:
            return None
        return json_res

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
    def list_contracts_csv(api_connection, parameters={}):
        logger.info("Listing contracts as CSV")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/csv/', parameters)
        return json_res

    @staticmethod
    def list_contracts_emir(api_connection, parameters={}):
        logger.info("Listing contracts on format for EMIR reporting")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contracts/emir/', parameters)
        return json_res

    @staticmethod
    def list_contracts_xml(api_connection, parameters={}):
        """Lists contracts with embedding

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: parameters to filter contracts
        :type parameters: str
        """
        logger.info("Listing contracts as XML")
        xmlres = api_connection.exec_get_url('/api/portfoliomanager/contracts/xmlelviz/', parameters)
        return xmlres
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
        if json_res is not None and "results" in json_res:
        #json_res=ContractsApi.list_contracts(api_connection, parameters)
            df = pd.DataFrame(data=json_res['results'])
            return df
        return None

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
    def get_contract_status(api_connection, enum):
        """Gets contract status from enum

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param enum: id of contract status
        :type enum: str, required
        """
        logger.info("Fetching contract status " + str(enum))
        json_res = api_connection.exec_get_url('/api/portfoliomanager/contractstatuses/' + str(enum) + "/")
        return json_res

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
