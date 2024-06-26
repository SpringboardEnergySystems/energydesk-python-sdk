import logging
import pandas as pd


logger = logging.getLogger(__name__)

class RiskLimitsApi:
    """Class for risk limits

    """
    @staticmethod
    def get_risk_categories(api_connection, params={}):
        """Fetching list of risk categories

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching risk categories")
        json_res=api_connection.exec_get_url('/api/creditrisk/rating/categoryrisklimits/', params)
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def post_risk_categories(api_connection, payload):
        """Fetching list of risk categories

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Posting risk limits")
        json_res=api_connection.exec_post_url('/api/creditrisk/rating/categoryrisklimits/', payload)
        if json_res is not None:
            return json_res
        return None
    
class RatingCategoryApi:
    """Class for risk limits

    """
    @staticmethod
    def get_rating_categories(api_connection, params={}):
        """Fetching list of risk categories

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching risk categories")
        json_res=api_connection.exec_get_url('/api/creditrisk/rating/category/', params)
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def post_rating_category(api_connection, payload):
        """Fetching list of risk categories

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Posting risk limits")
        json_res=api_connection.exec_post_url('/api/creditrisk/rating/category/', payload)
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def delete_rating_category(api_connection, payload):
        """Deleting risk category

        Args:
            api_connection (_type_): _description_
            payload (_type_): _description_
        """
        logger.info("Deleting risk limits")
        json_res=api_connection.exec_delete_url('/api/creditrisk/rating/category/', payload)
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def update_rating_category(api_connection, pk, payload):
        """Updating risk category

        Args:
            api_connection (_type_): _description_
            payload (_type_): _description_
        """
        logger.info("Update risk limits")
        json_res=api_connection.exec_patch_url('/api/creditrisk/rating/category/' + str(pk) + '/', payload)
        if json_res is not None:
            return json_res
        return None