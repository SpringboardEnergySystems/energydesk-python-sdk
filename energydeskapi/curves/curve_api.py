import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class CurveApi:
    """Class for price curves

    """
    # This function returns a single price (avg) for the period requested
    @staticmethod
    def get_period_price(api_connection, from_period, until_period, price_area, currency_code):
        """Fetches price within a period

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param from_period: period from
        :type from_period: str, required
        :param until_period: period to
        :type until_period: str, required
        :param price_area: price area
        :type price_area: str, required
        :param currency_code: specified currency (NOK, EUR, etc.)
        :type currency_code: str, required
        """
        logger.info("Fetching forward curve")
        qry_payload = {
            "price_area": price_area,
            "currency_code": currency_code,
            "period_from": from_period,
            "period_until": until_period,
        }
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/curvemanager/get-period-price/', qry_payload)
        if json_res is not None:
            curve_price = float(json_res['price'])
            return curve_price
        return 0


    @staticmethod
    def get_hourly_price_curve(api_connection , from_period, until_period, price_area, currency_code):
        """Fetches hourly price curve

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param from_period: period from
        :type from_period: str, required
        :param until_period: period to
        :type until_period: str, required
        :param price_area: price area
        :type price_area: str, required
        :param currency_code: specified currency (NOK, EUR, etc.)
        :type currency_code: str, required
        """
        logger.info("Fetching forward curve")
        qry_payload = {
            "price_area": price_area,
            "currency_code": currency_code,
            "period_from": from_period,
            "period_until": until_period,
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/curvemanager/get-forward-curve/', qry_payload)

        if json_res is not None:
            return json_res
        return None
