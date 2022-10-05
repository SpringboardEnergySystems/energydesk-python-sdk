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
class GoContract:
    """ Class for contracts

    """
    def __init__(self):
        self.pk=0
        self.main_contract=None
        self.certificates=None
        self.underlying_source=None
        self.energy_source = None
        self.invoice_date = None
        self.invoice_with_mva = None
        self.delivery_date=None
        self.certificates=[]

    def add_certificates(self, certificate):
        self.certificates.append({'period_from':convert_datime_to_utcstr(delivery_from),
                                'period_until':convert_datime_to_utcstr(delivery_until)})
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.underlying_source is not None: dict['underlying_source'] = self.underlying_source
        if self.main_contract is not None: dict['main_contract'] = self.main_contract
        if self.energy_source is not None: dict['energy_source'] = self.energy_source
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
    def upsert_contract(api_connection,
                          go_contract):
        """Registers GoO contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contracts: contracts to be registered
        :type contracts: str, required
        """
        logger.info("Registering contract")
        #print(format_money(price, locale='en_DE'))
        json_records=[]
        #json_records.append(contract.get_dict(api_connection))
        #json_res=api_connection.exec_post_url('/api/portfoliomanager/register-contracts/',json_records)
        json_res = api_connection.exec_post_url('/api/portfoliomanager/contracts/' + str(go_contract.pk) + "/", json_records)
        return json_res

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
    def get_certificates(api_connection):
        """Fetches certificates from server

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param contract_status_enum: status of contract
        :type contract_status_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/gos/certificates/')
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
        json_res = api_connection.exec_post_url('/api/gos/certificates/', payload)
        return json_res
