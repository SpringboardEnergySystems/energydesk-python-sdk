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

def convert_to_dataframe(dict):
    newdict=[]
    for rec in dict:
        newrec={'company':rec['company']}
        newrec['rating_date']=rec['rating_date']
        newrec['3M'] = rec['period_3M']
        newrec['1Y'] = rec['period_1Y']
        newrec['2Y'] = rec['period_2Y']
        newrec['3Y'] = rec['period_3Y']
        newrec['5Y'] = rec['period_5Y']
        newrec['7Y'] = rec['period_7Y']
        newrec['10Y'] = rec['period_10Y']
        newdict.append(newrec)
    df = pd.DataFrame.from_records(newdict)
    df.index = df.rating_date
    df.index = pd.to_datetime(df.index)
    return df

#  Change
class CounterPartsApi:
    """Class for counterparts

    """

    @staticmethod
    def upsert_credit_rating(api_connection, credit_rating):
        """Creates/Updates credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload=credit_rating.get_dict(api_connection)
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/counterparts/uploadratings/', payload)
        if success:
            return returned_data
        return None

    @staticmethod
    def get_credit_ratings(api_connection, parameters={}):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching ratings")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/ratings/', parameters)
        if json_res is not None:
            return json_res
        return None
    @staticmethod
    def get_credit_ratings_df(api_connection, parameters={}):
        """Fetches credit ratings for counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res=CounterPartsApi.get_credit_ratings(api_connection, parameters)
        if json_res is not None:
            return convert_to_dataframe(json_res)
        return None

    @staticmethod
    def get_counterparts(api_connection, parameters={}):
        """Fetches all counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_counterparts_df(api_connection, parameters={}):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url('/api/counterparts/counterparts/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def query_counterpart_exposure(api_connection,commodity_type_pk):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        payload={'commodity_type_pk':commodity_type_pk}
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/counterparts/counterpart-exposure/', payload)
        if success:
            return returned_data
        return None

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


