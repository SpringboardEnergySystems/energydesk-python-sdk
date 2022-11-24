import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change

class PortfolioViewsApi:
    """Class for tradingbooks

      """



    @staticmethod
    def get_product_view(api_connection, parameters={}):
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching product view")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/productview/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_product_view_df(api_connection, parameters={}):
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res = PortfolioViewsApi.get_product_view(api_connection, parameters)
        if json_res is None:
            return None
        if len(json_res)==0:
            return None
        df = pd.DataFrame(data=eval(json_res))

        return df

    @staticmethod
    def get_period_view(api_connection, parameters={}):
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching product view")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/periodview/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_period_view_df(api_connection, parameters={}):
        """Fetches specific product view

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res = PortfolioViewsApi.get_period_view(api_connection, parameters)
        if json_res is None:
            return None
        if len(json_res)==0:
            return None
        df = pd.read_json(json_res, orient="table")
        #df = pd.DataFrame(data=eval(json_res), orient)

        return df
