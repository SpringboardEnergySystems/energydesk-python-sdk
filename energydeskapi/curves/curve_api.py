import logging
import pandas as pd
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
logger = logging.getLogger(__name__)

class CurveApi:
    """Class for price curves

    """

    @staticmethod
    def get_curve_models(api_connection):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching curve models")
        json_res = api_connection.exec_get_url('/api/curvemanager/forwardcurvemodels/')
        return json_res
    @staticmethod
    def get_curve_models_df(api_connection):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching curve models")
        json_res = api_connection.exec_get_url('/api/curvemanager/forwardcurvemodels/')
        df = pd.DataFrame(data=json_res)
        return df

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


    @staticmethod
    def upload_forward_curve(api_connection ,price_date, price_area,
                                currency_code, forward_curve_model,
                                period_prices,
                                period_resolution=PeriodResolutionEnum.HOURLY.value,
                               market_name="Nordic Power"):

        payload={
            'market_name': market_name,
            'price_date': price_date,
            'price_area':price_area,
            'forward_curve_model': forward_curve_model,
            'period_resolution':period_resolution,
            'currency_code':currency_code,
            'periods':period_prices#period_prices_df.to_json(orient='records',date_format='iso')
        }
        print(price_area)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/curvemanager/upload-forwardcurve/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_latest_forward_curve(api_connection, parameters={}):
        """Fetches all companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res=api_connection.exec_get_url('/api/curvemanager/forwardcurves/latest/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def retrieve_latest_forward_curve(api_connection , price_area,
                                currency_code, forward_curve_model,
                                period_resolution=PeriodResolutionEnum.DAILY.value,
                               market_name="Nordic Power"):

        payload={
            'market_name': market_name,
            'price_area':price_area,
            "period_resolution":period_resolution,
            'forward_curve_model': forward_curve_model,
            'currency_code':currency_code,
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/curvemanager/retrieve-forwardcurve/', payload)
        return success, json_res, status_code, error_msg



    @staticmethod
    def retrieve_latest_forward_curve_df(api_connection , price_area,
                                currency_code, forward_curve_model,
                                period_resolution=PeriodResolutionEnum.DAILY.value,
                               market_name="Nordic Power"):


        success, json_res, status_code, error_msg = CurveApi.retrieve_latest_forward_curve(api_connection, price_area,
                                currency_code, forward_curve_model,period_resolution,market_name)
        if success:
            df = pd.DataFrame(data=eval(json_res))
            df.index = df['period_from']
            df=convert_dataframe_to_localtime(df)
            return success, df, status_code, error_msg
        else:
            success, None, status_code, error_msg

