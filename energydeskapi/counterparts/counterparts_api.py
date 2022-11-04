import requests
import json
import logging
import pandas as pd


logger = logging.getLogger(__name__)

class CounterPartRating:
    def __init__(self, name, rating_date, record):
        self.name=name
        self.record=record
        self.rating_date=rating_date

    def get_dict(self, api_conn):
        dict = {}
        dict['company']=self.name
        dict['rating_date'] = self.rating_date
        dict['period_3M'] = self.record['3M']
        dict['period_1Y'] = self.record['1Y']
        dict['period_2Y'] = self.record['2Y']
        dict['period_3Y'] = self.record['3Y']
        dict['period_5Y'] = self.record['5Y']
        dict['period_7Y'] = self.record['7Y']
        dict['period_10Y'] = self.record['10Y']
        return dict


#  Change
class CounterPartsApi:
    """Class for counterparts

    """

    def upsert_credit_rating(api_connection, credit_rating):
        payload=credit_rating.get_dict(api_connection)
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/counterparts/uploadratings/', payload)
        if success:
            return returned_data
        return None
    @staticmethod
    def get_counterparts(api_connection):
        """Fetches all counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_counterparts_df(api_connection):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def upsert_counterparts(api_connection, payload):
        """Registers counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Upserting counterparts")
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/counterparts/counterparts/', payload)
        if success:
            return returned_data
        return None


