import requests
import json
import logging
import pandas as pd
from energydeskapi.sdk.money_utils import gen_json_money
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.assets.assets_api import AssetsApi
from moneyed.l10n import format_money
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr
from datetime import datetime
logger = logging.getLogger(__name__)
#  Change
class GoContract:
    """ Class for contracts

    """
    def __init__(self):
        self.pk=0
        self.main_contract=None
        self.certificates=None
        self.extra_info = None
        self.underlying_source=None
        self.energy_source = None
        self.invoice_date = None
        self.invoice_with_mva = None
        self.delivery_date=None
        self.certificates=[]

    def add_certificates(self, certificate):
        self.certificates.append(certificate)

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.underlying_source is not None: dict['underlying_source'] = self.underlying_source
        if self.main_contract is not None: dict['main_contract'] = self.main_contract.get_dict(api_conn)
        if self.energy_source is not None: dict['energy_source'] = self.energy_source
        if self.extra_info is not None: dict['extra_info'] = self.extra_info
        if self.invoice_with_mva is not None: dict['invoice_with_mva'] = self.invoice_with_mva
        if self.invoice_date is not None: dict['invoice_date'] = self.invoice_date
        if self.delivery_date is not None: dict['delivery_date'] = self.delivery_date
        if len(self.certificates)>0:
            dict['certificates']=self.certificates

        return dict
class GosApi:
    """Class for contracts in api

    """

    @staticmethod
    def lookup_go_contract_pk(api_connection,
                          contract_pk):
        json_res=api_connection.exec_get_url('/api/gos/contractlookup?contract_pk=' + str(contract_pk))
        print(json_res)
        if json_res is not None:
            return json_res['results'][0]
        return None

    @staticmethod
    def upsert_contract(api_connection,
                          go_contract):
        """Registers GoO contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contracts: contracts to be registered
        :type contracts: str, required
        """

        if go_contract.pk>0:
            success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/gos/gocontracts/' + str(go_contract.pk) + "/", go_contract.get_dict(api_connection))
        else:
            #print(json.dumps(go_contract.get_dict(api_connection), indent=2))
            success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/gos/gocontracts/',go_contract.get_dict(api_connection))
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_certificate_url(api_connection, certificate_pk):
        """Fetches url for certificates

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param certificate_pk: type of contract
        :type certificate_pk: integer, required
        """
        return api_connection.get_base_url() + '/api/gos/certificates/' + str(certificate_pk) + "/"
    @staticmethod
    def get_contracts_embedded(api_connection, parameters={}):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/gos/gocontracts/embedded/', parameters)
        return json_res
    @staticmethod
    def get_contracts(api_connection, parameters={}):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/gos/gocontracts/', parameters)
        return json_res
    @staticmethod
    def get_contract(api_connection, go_contract_pk):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/gos/gocontracts/' + str(go_contract_pk) + "/")
        return json_res
    @staticmethod
    def get_certificates(api_connection, parameters={}):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/gos/certificates/', parameters)
        return json_res

    @staticmethod
    def get_certificates_df(api_connection, parameters={}):
        """Fetches all companies in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching companylist")
        parameters['page_size']=1000
        json_res=GosApi.get_certificates(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res["results"])
        return df

    @staticmethod
    def get_certificate_by_key(api_connection, key):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/gos/certificates/' + str(key) + "/")
        return json_res


    @staticmethod
    def get_energysource_by_key(api_connection, energy_source_enum):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        esource_key = energy_source_enum if isinstance(energy_source_enum, int) else energy_source_enum.value
        json_res = api_connection.exec_get_url('/api/gos/energysources/' + str(esource_key) + "/")
        return json_res

    @staticmethod
    def register_certificate(api_connection, certificate, description):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        payload={
            "shortname":certificate,
            "description":description
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/gos/certificates/', payload)
        return json_res

    @staticmethod
    def get_source_collection_url(api_connection, source_collection_pk):
        """Fetches url for certificates

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param certificate_pk: type of contract
        :type certificate_pk: integer, required
        """
        return api_connection.get_base_url() + '/api/gos/sourcecollection/' + str(source_collection_pk) + "/"
    @staticmethod
    def get_source_collections(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/gos/sourcecollection/', parameters)
        return json_res
    @staticmethod
    def get_source_collections_embedded(api_connection, parameters={}):
        logger.info("Fetching source collection")
        #parameters['page_size']=1000
        json_res = api_connection.exec_get_url('/api/gos/sourcecollection/embedded/', parameters)
        #json_res=GosApi.get_source_collections(api_connection, parameters)
        return json_res


    @staticmethod
    def register_source_collection(api_connection, local_area_pk, asset_list):
        """Registers a souce collection

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param local_area_pk: Key for local aeea
        :type local_area_pk: integer, required
        :param asset_list: list of asset primary keys
        :type asset_list: lst, required
        """
        asset_url_list=[]
        for a in asset_list:
            asset_url_list.append(AssetsApi.get_asset_url(api_connection, a))

        payload={
            "local_area": LocationApi.get_local_area_url(api_connection, local_area_pk),
            "assets_in_area":asset_url_list
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/gos/sourcecollection/', payload)
        return json_res
    @staticmethod
    def get_source_data(api_connection,parameters={}):
        json_res=api_connection.exec_get_url('/api/gos/sourcedata/', parameters)
        if json_res is not None:
            return json_res
        return None