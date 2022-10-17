import requests
import json
import logging
import pandas as pd
import pytz
logger = logging.getLogger(__name__)

class SpotPricesApi:
    """Class for spot prices

    """

    @staticmethod
    def get_spot_prices(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/spotprices/', parameters)
        if json_res is None:
            return None
        print(json_res)
        return json_res

    @staticmethod
    def get_spot_prices_df(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/spotprices/', parameters)
        if json_res is None:
            return None
        df = pd.read_json(json_res, orient='records')
        df.index = pd.to_datetime(df["datetimehour"])
        df.index = df.index.tz_convert('Europe/Oslo')
        df.datetimehour=df.index

        return df

