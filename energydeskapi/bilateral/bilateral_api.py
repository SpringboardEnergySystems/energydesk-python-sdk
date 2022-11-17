import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class BilateralApi:
    """Class for price curves

    """

    @staticmethod
    def calculate_contract_price(api_connection ,periods, contract_mw, price_area, currency_code, curve_model_key,
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
        logger.info("Calculate bilateral price")

        dict_periods=[]
        for p in periods:
            dict_periods.append({
            "contract_date_from":p[0],
            "contract_date_until": p[1],
            })
        qry_payload = {
            "forward_curve":{
                    "price_area": price_area,
                    "currency_code": currency_code,
                    "curve_model_key":curve_model_key,
                    },
            "periods":dict_periods,
            "contract_mw": contract_mw
        }
        if param_int_1 is not None:
            qry_payload['forward_curve']['param_int_1']= param_int_1
        if param_int_2 is not None:
            qry_payload['forward_curve']['param_int_2']= param_int_2
        if param_int_3 is not None:
            qry_payload['forward_curve']['param_int_3']= param_int_3
        if param_int_4 is not None:
            qry_payload['forward_curve']['param_int_4']= param_int_4
        if param_str_1 is not None:
            qry_payload['forward_curve']['param_str_1']= param_str_1
        if param_str_2 is not None:
            qry_payload['forward_curve']['param_str_2']= param_str_2
        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/', qry_payload)
        return success, json_res, status_code, error_msg
