import logging
from typing import Optional

import pandas as pd
from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)

class SpotPricesApi:
    """Class for spot prices

    """

    @staticmethod
    def get_spot_prices(api_connection: ApiConnection, parameters: dict={}) -> Optional[list[dict]]:
        json_res = api_connection.exec_get_url('/api/markets/spotprices/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_spot_prices_df(api_connection: ApiConnection, parameters: dict={}) -> Optional[pd.DataFrame]:
        json_res = api_connection.exec_get_url('/api/markets/spotprices/', parameters)
        if json_res is None:
            return None
        #df = pd.read_json(json_res, orient='records')
        if isinstance(json_res, str):
            import io
            df = pd.read_json(io.StringIO(json_res), orient='records')
        else:
            df = pd.DataFrame(json_res)
        if len(df)==0:
            logger.error("No spot prices found")
            return None
    
        df.index = pd.to_datetime(df["datetimehour"])
        df.index = df.index.tz_convert('Europe/Oslo')
        df.datetimehour=df.index

        return df

