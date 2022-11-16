import requests
import json
import logging
import pandas as pd
from energydeskapi.sdk.common_utils import check_fix_date2str
logger = logging.getLogger(__name__)

class PricingApi:
    """Class for price calculation

    """

    @staticmethod
    def calc_collars(api_connection, price_area, currency, price_min, price_max,
                                                  date_from, number_of_months, interest_rate,
                                                  volatility):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Calc Collar")
        payload={
            'currency':currency,
            'price_area':price_area,
            'number_of_months': number_of_months,
            'price_min': price_min,
            'price_max': price_max,
            'date_from': check_fix_date2str(date_from),
            'interest_rate': interest_rate,
            'volatility': volatility
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calccollars/', payload)
        print(error_msg)
        return success, json_res, status_code, error_msg
