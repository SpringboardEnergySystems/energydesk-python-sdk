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

    @staticmethod
    def calc_covariance_var(api_connection, trading_books=[], days_back=40):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Calc Covariance Var")
        payload={
            'price_days':days_back,
            'trading_books':trading_books
        }
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calccovariancevar/', payload)
        #print(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calc_covariance_var_df(api_connection, trading_books=[], days_back=40):
        success, json_res, status_code, error_msg=RiskApi.calc_covariance_var(api_connection, trading_books, days_back)
        if success ==False:
            return None
        print(json_res)
        #df=pd.DataFrame(data=eval(json_res))
        return None