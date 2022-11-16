import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class RiskApi:
    """Class for price curves

    """

    @staticmethod
    def calc_volatilities(api_connection, months_back, price_areas):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Calc Volatilities")
        payload={
            'months_back':months_back,
            'price_areas':price_areas
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calcvolatilities/', payload)
        print(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calc_volatilities_df(api_connection, months_back, price_areas):
        success, json_res, status_code, error_msg=RiskApi.calc_volatilities(api_connection, months_back, price_areas)
        if success ==False:
            return None
        df=pd.DataFrame(data=eval(json_res))
        return df