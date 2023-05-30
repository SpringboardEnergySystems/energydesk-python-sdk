import logging
import pandas as pd
from energydeskapi.customers.customers_api import Company, CustomersApi
logger = logging.getLogger(__name__)


class SystemApi:
    """Class for System API

    """

    @staticmethod
    def get_system_features(api_connection):
        """Fetches system features

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching system features")
        json_res = api_connection.exec_get_url(
            '/api/system/systemfeatures/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_system_feature_by_key(api_connection, pk):
        """Fetches system feature by key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching system feature " + str(pk))
        json_res = api_connection.exec_get_url(
            '/api/system/systemfeatures/' + str(pk) + '/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_system_feature_url(api_connection, pk):
        """Fetches user from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of system feature
        :type pk: str, required
        """
        return api_connection.get_base_url() + '/api/system/systemfeatures/' + str(pk) + "/"

    @staticmethod
    def get_system_access_types(api_connection):
        """Fetches system access types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching system access types")
        json_res = api_connection.exec_get_url(
            '/api/system/systemaccesstypes/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_system_access_type_by_key(api_connection, pk):
        """Fetches system access type by key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of access type
        :type pk: str, required
        """
        logger.info("Fetching system access type " + str(pk))
        json_res = api_connection.exec_get_url(
            '/api/system/systemaccesstypes/' + str(pk) + '/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_system_access_type_url(api_connection, pk):
        """Fetches user from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of access type
        :type pk: str, required
        """
        return api_connection.get_base_url() + '/api/system/systemaccesstypes/' + str(pk) + "/"



    @staticmethod
    def get_system_manager(api_connection):
        """Fetches user from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required

        """
        json_res = api_connection.exec_get_url(
            '/api/system/systemmanager/embedded/')
        if json_res is not None:
            return json_res
        return None


    @staticmethod
    def upsert_system_manager(api_connection, system_owner_pk, system_manager_pk):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        system_owner_url=CustomersApi.get_company_url(api_connection, system_owner_pk)
        system_manager_url = CustomersApi.get_company_url(api_connection, system_manager_pk)
        payload={
            'description': "",
            'sysadmin': system_manager_url,
            'sysowner': system_owner_url,
        }
        print(payload)

        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/system/systemmanager/', payload)

        return success, returned_data, status_code, error_msg
