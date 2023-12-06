import logging
import pandas as pd
import json

logger = logging.getLogger(__name__)
#  Change

class SettlementApi:
    """Class for settlement api

      """


    @staticmethod
    def get_settlement_data(api_connection, payload={}):
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching settlement view", payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/settlement/exportinvoicedata/', payload)
        return json_res

    @staticmethod
    def get_settlement_view(api_connection, parameters={}):
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching settlement view")
        json_res = api_connection.exec_get_url('/api/settlement/settlementview/', parameters)
        if json_res is None:
            return None, None
        if len(json_res['view_data'])==0:
            return None, None
        view_id=json_res['view_id']
        view_data = json_res['view_data']
        return view_id, view_data

    @staticmethod
    def get_settlement_view_df(api_connection, parameters={}):


        id, json_res = SettlementApi.get_settlement_view(api_connection, parameters)

        if json_res is None:
            return None, None

        df = pd.read_json(json_res, orient="table")

        return id, df
