import requests
import json
import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change
class TradingBooksApi:
    """Description...

      """

    @staticmethod
    def fetch_tradingbooks(api_connection):
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbook/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def load_tradingbook_by_pk(api_connection, pk):
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbook/')
        for r in json_res:
            if r['pk']==pk:
                return r
        return None