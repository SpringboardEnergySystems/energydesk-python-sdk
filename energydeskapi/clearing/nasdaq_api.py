import json
import logging
import pandas as pd

import ast
logger = logging.getLogger(__name__)
#  Change
class NasdaqApi:
    """Class for clearing reports

    """


    @staticmethod
    def get_traderecords(api_connection, parameters={}):
        """Fetches a list of embedded clearing report records

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching trade records from nasdaq table")
        json_res = api_connection.exec_get_url('/api/elvizmapping/nasdaqtradedata/', parameters)
        if json_res is None:
            return None
        all_record = []
        df=pd.DataFrame(json_res)
        print(df)
        return df


