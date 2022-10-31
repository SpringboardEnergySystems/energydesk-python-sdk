import requests
import json
import logging
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi

logger = logging.getLogger(__name__)
#  Change
class CounterPartsApi:
    """Class for counterparts

    """

    @staticmethod
    def get_counterparts(api_connection):
        """Fetches all counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching treasury bank list")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/')
        print(json_res)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_counterparts_df(api_connection):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching treasury bank list")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df


