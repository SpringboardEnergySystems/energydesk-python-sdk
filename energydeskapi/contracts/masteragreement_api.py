import logging
import pandas as pd


logger = logging.getLogger(__name__)

class MasterContractAgreement:
    def __init__(self):
        self.pk = 0
        self.title = None
        self.created_at = None
        self.contract_owner = None
        self.counterpart = None
        self.contract_info_1 = None
        self.contract_info_2 = None
        self.contract_info_3 = None
        self.signed_contract_url_ref = None

    def get_dict(self, api_conn):
        dict = {}
        dict['pk']=self.pk
        if self.title is not None: dict['title'] = self.title
        if self.created_at is not None: dict['created_at'] = self.created_at
        if self.contract_owner is not None: dict['contract_owner'] = self.contract_owner
        if self.counterpart is not None: dict['counterpart'] = self.counterpart
        if self.contract_info_1 is not None: dict['contract_info_1'] = self.contract_info_1
        if self.contract_info_2 is not None: dict['contract_info_2'] = self.contract_info_2
        if self.contract_info_3 is not None: dict['contract_info_3'] = self.contract_info_3
        if self.signed_contract_url_ref is not None: dict['signed_contract_url_ref'] = self.signed_contract_url_ref
        return dict

class MasterAgreementApi:
    """Class for Master contract agreements API

    """

    @staticmethod
    def get_master_agreement(api_connection, parameters={}):
        """Fetches master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching master agreement")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/mastercontractagreement/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def register_master_agreement(api_connection, master_agreement):
        """Creates master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param master_agreement: master contract agreement object
        :type master_agreement: str, required
        """
        payload = master_agreement.get_dict(api_connection)
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/mastercontractagreement/', payload)
        if success:
            return returned_data
        return None
