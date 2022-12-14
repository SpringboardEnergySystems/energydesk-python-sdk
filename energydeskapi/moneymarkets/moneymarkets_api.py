import logging
import pandas as pd
import pytz
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
logger = logging.getLogger(__name__)

class MoneyMarketsApi:
    """ Class for assets

    """

    @staticmethod
    def get_fxspot(api_connection):
        """Fetches fxspot

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fxspot/')
        if json_res is None:
            return None
        df = pd.DataFrame(eval(json_res))
        return df

    @staticmethod
    def get_fxtenors(api_connection):
        """Fetches fxtenors

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fxtenors/')
        if json_res is None:
            return None
        df = pd.DataFrame(eval(json_res))
        return df

    @staticmethod
    def get_yieldcurves(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/yieldcurves/', parameters)
        return json_res

    @staticmethod
    def get_yieldcurves_df(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/yieldcurves/', parameters)
        if json_res is None:
            return None
        norzone = pytz.timezone('Europe/Oslo')
        df = pd.DataFrame(eval(json_res))
        df['date'] = df['date'].astype('datetime64[ns]')
        df['date'] = df['date'].dt.tz_localize(tz=norzone)
        df.index = df['date']
        df['timestamp'] = df['date']
        df = convert_dataframe_to_localtime(df)

        return df
    @staticmethod
    def get_fwdrates(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fwdrates/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(eval(json_res))
        return df

