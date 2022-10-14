import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class MoneyMarketsApi:
    """ Class for assets

    """

    @staticmethod
    def get_fxblablabla(api_connection, parameters={}):
        """Fetches all assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assets/', parameters)
        if json_res is None:
            return None
        return json_res
        # json_res = api_connection.exec_get_url('/api/assets/assets/')
        # if json_res is None:
        #     return None
        # return json_res
