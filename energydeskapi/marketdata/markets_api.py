import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class MarketsApi:
    """Class for user profiles and companies

    """

    @staticmethod
    def get_market_url(api_connection, market_enum):
        return api_connection.get_base_url() +'/api/markets/markets/' + str(market_enum.value) + "/"
    @staticmethod
    def get_market_obj(api_connection, market_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/markets/' + str(market_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_instrument_type_url(api_connection, instrument_type_enum):
        return api_connection.get_base_url() +'/api/markets/instrumenttypes/' + str(instrument_type_enum.value) + "/"
    @staticmethod
    def get_instrument_type_obj(api_connection, instrument_type_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/instrumenttypes/' + str(instrument_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_commodity_type_url(api_connection, commodity_type_enum):
        comm_type = commodity_type_enum if isinstance(commodity_type_enum, int) else commodity_type_enum.value
        return api_connection.get_base_url() +'/api/markets/commoditytypes/' + str(comm_type) + "/"

    @staticmethod
    def get_commodity_type_obj(api_connection, commodity_type_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditytypes/' + str(commodity_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_blocksize_category_url(api_connection, blocksize_category_enum):
        return api_connection.get_base_url() +'/api/markets/blocksizecategories/' + str(blocksize_category_enum.value) + "/"

    @staticmethod
    def get_blocksize_category_obj(api_connection, blocksize_category_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/blocksizecategories/' + str(blocksize_category_enum.value) + "/")
        if json_res is None:
            return None
        return json_res
