import pendulum

import logging
import pandas as pd
logger = logging.getLogger(__name__)


class FlexibilityOptimizationApi:
    """ Class for assets

    """

    @staticmethod
    def optimize_flexibility(api_connection, parameters):
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexoptimizer/optimizeassets/', parameters)
        if json_res is None:
            logger.error("Problems optimizing battery " + str(error_msg))
        else:
            logger.info("Assets optimized")
        return success, json_res, status_code, error_msg
