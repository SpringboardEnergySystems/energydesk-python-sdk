import pendulum

import logging
import pandas as pd
from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)


class FlexibilityOptimizationApi:
    """ Class for assets

    """

    @staticmethod
    def optimization_price_data(api_connection: ApiConnection, parameters):
        json_res = api_connection.exec_get_url('/api/flexoptimizer/optimpricedata/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def optimize_max_usage(api_connection: ApiConnection, parameters):
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexoptimizer/optimizemaxusage/', parameters)
        if json_res is None:
            logger.error("Problems optimizing battery " + str(error_msg))
        else:
            logger.info("Assets optimized")
        return success, json_res, status_code, error_msg

    @staticmethod
    def optimize_armed_availability(api_connection: ApiConnection, parameters):
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexoptimizer/armedavailability/', parameters)
        if json_res is None:
            logger.error("Problems optimizing availability " + str(error_msg))
        else:
            logger.info("Optimized availability")
        return success, json_res, status_code, error_msg