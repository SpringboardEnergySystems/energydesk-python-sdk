import logging
import pandas as pd


logger = logging.getLogger(__name__)

class RiskLimitsApi:
    """Class for credit risk

    """
    @staticmethod
    def get_risk_categories(api_connection, params={}):
        """Fetching list of risk categories

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companies")
        json_res=api_connection.exec_get_url('/api/creditrisk/rating/risklimits/', params)
        if json_res is not None:
            return json_res
        return None