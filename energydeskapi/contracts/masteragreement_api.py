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
        self.contract_info = None
        self.phone = None
        self.email = None
        self.email_contract_documents = False
        self.signed_contract_url_ref = None

    def get_dict(self, api_conn):
        dict = {}
        dict['pk']=self.pk
        if self.title is not None: dict['title'] = self.title
        if self.created_at is not None: dict['created_at'] = self.created_at
        if self.contract_owner is not None: dict['contract_owner'] = self.contract_owner
        if self.counterpart is not None: dict['counterpart'] = self.counterpart
        if self.contract_info is not None: dict['contract_info'] = self.contract_info
        if self.phone is not None: dict['phone'] = self.phone
        if self.email is not None: dict['email'] = self.email
        if self.email_contract_documents is not False: dict['email_contract_documents'] = self.email_contract_documents
        if self.signed_contract_url_ref is not None: dict['signed_contract_url_ref'] = self.signed_contract_url_ref
        return dict

class MasterAgreementApi:
    """Class for Master contract agreements API

    """

    @staticmethod
    def get_master_agreements(api_connection, parameters={}):
        """Fetches master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching master agreement")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/mastercontractagreements/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_master_agreements_embedded(api_connection, parameters={}):
        """Fetches master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching master agreement")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/mastercontractagreements/embedded/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_master_agreements_by_key(api_connection, masteragreement_pk):
        """Fetches master contract agreement from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param masteragreement_pk: key to master contract agreement
        :type masteragreement_pk: required
        """
        logger.info("Loading master agreement with pk " + str(masteragreement_pk))
        json_res = api_connection.exec_get_url('/api/portfoliomanager/mastercontractagreements/'
                                               + str(masteragreement_pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_master_agreement(api_connection, master_agreement):
        """Creates/Updates master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param master_agreement: master contract agreement object
        :type master_agreement: str, required
        """
        logger.info("Upserting master agreement")
        payload = master_agreement.get_dict(api_connection)
        key = int(payload['pk'])
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/portfoliomanager/mastercontractagreements/' + payload['pk'] + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/portfoliomanager/mastercontractagreements/', payload)
        if success:
            return returned_data
        return None
