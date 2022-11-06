import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class CurveApi:
    """Class for price curves

    """


    @staticmethod
    def generate_forward_curve(api_connection ,period_from, period_until, price_area, currency_code, curve_model_key,
                               param_int_1=None,param_int_2=None,param_int_3=None,param_int_4=None,
                               param_str_1=None,param_str_2=None):
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
            "period_from": period_from,
            "period_until": period_until,
            "curve_model_key":curve_model_key,
        }
        if param_int_1 is not None:
            qry_payload['param_int_1']= param_int_1
        if param_int_2 is not None:
            qry_payload['param_int_2']= param_int_2
        if param_int_3 is not None:
            qry_payload['param_int_3']= param_int_3
        if param_int_4 is not None:
            qry_payload['param_int_4']= param_int_4
        if param_str_1 is not None:
            qry_payload['param_str_1']= param_str_1
        if param_str_2 is not None:
            qry_payload['param_str_2']= param_str_2
        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/curvemanager/generate-forwardcurve/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def generate_forward_curve_df(api_connection ,period_from, period_until, price_area, currency_code, curve_model_key,
                               param_int_1=None,param_int_2=None,param_int_3=None,param_int_4=None,
                               param_str_1=None,param_str_2=None):
        success, json_res, status_code, error_msg=CurveApi.generate_forward_curve(api_connection,
                    period_from, period_until, price_area, currency_code, curve_model_key,
                    param_int_1,param_int_2,param_int_3,param_int_4, param_str_1,param_str_2)
        if json_res is not None:
            df = pd.DataFrame(data=eval(json_res))
            return success, df, status_code, error_msg
        return success, None, status_code, error_msg