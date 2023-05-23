import logging
import pandas as pd
import pytz
from energydeskapi.sdk.common_utils import safe_prepare_json
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
logger = logging.getLogger(__name__)

class MoneyMarketsApi:
    """ Class for assets

    """

    @staticmethod
    def get_fxspot(api_connection, parameters={}):
        """Fetches fxspot

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fxspot/', parameters)
        if json_res is None:
            return None, None
        currency_date = json_res['currency_date']
        dataframe=json_res['dataframe']
        df = None if dataframe is None else pd.DataFrame(data=safe_prepare_json(dataframe))
        return currency_date, df

    @staticmethod
    def get_fxtenors(api_connection, parameters={}):
        """Fetches fxtenors

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fxtenors/', parameters)
        if json_res is None:
            return None, None
        currency_date = json_res['currency_date']
        dataframe=json_res['dataframe']
        df = None if dataframe is None else pd.DataFrame(data=safe_prepare_json(dataframe))
        return currency_date, df

    @staticmethod
    def get_yieldcurves(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/yieldcurves/', parameters)
        if json_res is None:
            return None,None
        currency_date = json_res['currency_date']
        jdata=json_res['dataframe']
        return currency_date, jdata

    @staticmethod
    def get_yieldcurves_df(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/yieldcurves/', parameters)
        if json_res is None:
            return None, None
        currency_date = json_res['currency_date']
        dataframe=json_res['dataframe']
        print(dataframe)
        df = None if dataframe is None else pd.DataFrame(data=safe_prepare_json(dataframe))
        if df is None or len(df.index)==0:
            return currency_date, df
        norzone = pytz.timezone('Europe/Oslo')
        df['date'] = df['date'].astype('datetime64[ns]')
        df['date'] = df['date'].dt.tz_localize(tz=norzone)
        df.index = df['date']
        df['timestamp'] = df['date']
        df = convert_dataframe_to_localtime(df)

        return currency_date, df
    @staticmethod
    def get_fwdrates(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fwdrates/', parameters)
        if json_res is None:
            return None, None
        currency_date = json_res['currency_date']
        dataframe=json_res['dataframe']
        df = None if dataframe is None else pd.DataFrame(data=safe_prepare_json(dataframe))
        return currency_date, df

    @staticmethod
    def get_fwd_curves(api_connection, parameters={}):
        """Fetches yieldcurves

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/currencies/fwdrates/curves/', parameters)
        if json_res is None:
            return None, None
        currency_date = json_res['currency_date']
        dataframe=json_res['dataframe']
        df = None if dataframe is None else pd.DataFrame(data=safe_prepare_json(dataframe))
        return currency_date, df

