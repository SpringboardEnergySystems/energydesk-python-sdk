import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class LemsApi:
    """Class for price curves

    """
    @staticmethod
    def get_ticker_data(api_connection, parameters={}):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url('/api/lems/tickerdata', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_traded_products(api_connection, parameters={}):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url('/api/lems/localproducts/compact/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def add_order(api_connection, ticker, price, quantity, buy_or_sell):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "order_id":"",
            "order_timestamp":"2022-01-23",
            "ticker":ticker,
            "price":price,
            "quantity": quantity,
            "buy_or_sell":buy_or_sell
        }
        logger.info("Enter orde")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorder/', payload)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

