import io
import logging
from typing import Any, Optional

import pandas as pd

from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)
#  Change

class SettlementApi:
    """Class for settlement api

      """


    @staticmethod
    def get_settlement_data(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> list[dict]:
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching settlement view", parameters)
        res = api_connection.exec_get_url(
            '/api/settlement/exportinvoicedata/', parameters)
        return res

    @staticmethod
    def get_settlement_view(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[str]]:
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
    def get_settlement_view_df(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[pd.DataFrame]]:


        id, data = SettlementApi.get_settlement_view(api_connection, parameters)

        if data is None:
            return None, None
        if isinstance(data, str):
            return id, pd.read_json(io.StringIO(data), orient="table")
        df = pd.read_json(data, orient="table")
        return id, df

    @staticmethod
    def get_period_result_view(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[str]]:
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching settlement view")
        json_res = api_connection.exec_get_url('/api/settlement/settlementview/periodresults/', parameters)
        if json_res is None:
            return None, None
        if len(json_res['view_data'])==0:
            return None, None
        view_id=json_res['view_id']
        view_data = json_res['view_data']
        return view_id, view_data

    @staticmethod
    def get_period_position_and_result_view(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching settlement view")
        json_res = api_connection.exec_get_url('/api/settlement/settlementview/periodresults/', parameters)
        if json_res is None:
            return None, None, None
        if len(json_res['view_data'])==0:
            return None, None, None
        view_id=json_res['view_id']
        view_data = json_res['view_data']
        positionview_data = json_res['positionview_data']
        return view_id, view_data, positionview_data

    @staticmethod
    def get_period_result_view_csv(api_connection: ApiConnection, parameters: dict={}):
        data = api_connection.exec_get_url('/api/settlement/settlementview/periodresultscsv/', parameters)
        return data

    @staticmethod
    def get_period_result_view_df(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[pd.DataFrame]]:

        id, json_res = SettlementApi.get_period_result_view(api_connection, parameters)
        if json_res is None:
            return None, None
        df = pd.read_json(json_res, orient="table")
        return id, df

    @staticmethod
    def get_product_result_view(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[str]]:
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching product settlement view")
        json_res = api_connection.exec_get_url('/api/settlement/settlementview/productresults/', parameters)
        if json_res is None:
            return None, None
        if len(json_res['view_data'])==0:
            return None, None
        view_id=json_res['view_id']
        view_data = json_res['view_data']
        return view_id, view_data

    @staticmethod
    def get_product_result_view_df(api_connection: ApiConnection, parameters: dict[str, Any]={}) -> tuple[Optional[str], Optional[pd.DataFrame]]:
        id, json_res = SettlementApi.get_product_result_view(api_connection, parameters)
        if json_res is None:
            return None, None
        df = pd.read_json(json_res, orient="table")
        return id, df