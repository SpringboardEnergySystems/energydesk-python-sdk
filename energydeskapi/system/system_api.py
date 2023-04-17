import logging
import pandas as pd

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
        """
        logger.info("Fetching system access type " + str(pk))
        json_res = api_connection.exec_get_url(
            '/api/system/systemaccesstypes/' + str(pk) + '/')
        if json_res is not None:
            return json_res
        return None
