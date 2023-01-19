import logging
import pandas as pd
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from datetime import datetime, timedelta, timezone
import pytz
from dateutil import relativedelta
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
logger = logging.getLogger(__name__)

class BilateralApi:
    """Class for price curves

    """

    @staticmethod
    def calculate_deliveries(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value):
        qry_payload = {
                "period_from": period_from,
                "period_until": period_until,
                "resolution":resolution,
        }

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/deliveries/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_deliveries_df(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value):

        success, json_res, status_code, error_msg = BilateralApi.calculate_deliveries(api_connection ,period_from, period_until, resolution)
        if success==False:
            return success, None, None, status_code, error_msg
        deliveries=json_res['bilateral_deliveries']
        df_deliveries = pd.DataFrame(data=eval(deliveries))
        df_deliveries.index = df_deliveries['period_from']
        print(df_deliveries)
        trades = json_res['bilateral_trades']
        df_trades = pd.DataFrame(data=eval(trades))
        print("GOOD#",df_trades)
        #df_deliveries = convert_dataframe_to_localtime(df_deliveries)
        return True, df_deliveries,df_trades, status_code, error_msg

    @staticmethod
    def calculate_contract_price(api_connection ,periods, price_area, currency_code,
                                 curve_model,curve_resolution=PeriodResolutionEnum.DAILY.value,
                                 wacc=0.06, inflation=0,
                                 profile_type="BASELOAD", monthly_profile=[],
                                 weekday_profile=[],hours=list(range(24))):
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
            "period_tag": p[0],
            "contract_date_from":p[1],
            "contract_date_until": p[2],
            })
        qry_payload = {
                "price_area": price_area,
                "currency_code": currency_code,
                "curve_model":curve_model,
                "wacc":wacc,
                "inflation":inflation,
                "curve_resolution":curve_resolution,
                "periods":dict_periods,
                "contract_type":profile_type,
                "monthly_profile":monthly_profile,
                "weekday_profile": weekday_profile,
                "day_profile": hours
        }

        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_contract_price_df(api_connection, periods, price_area, currency_code,
                                    curve_model,curve_resolution=PeriodResolutionEnum.MONTHLY.value,
                                    wacc=0.06, inflation=0,
                                 profile_type="BASELOAD", monthly_profile=[], weekday_profile=[], hours=list(range(24))):

        print(periods, price_area, currency_code, curve_model,curve_resolution)
        success, json_res, status_code, error_msg=BilateralApi.calculate_contract_price(api_connection, periods, price_area,
                                                                                        currency_code, curve_model,curve_resolution,
                                 wacc, inflation,profile_type, monthly_profile, weekday_profile, hours)
        if success:
            period_prices = json_res['period_prices']
            df_curve = pd.DataFrame(data=eval(json_res['forward_curve']))
            df_curve.index=df_curve['date']
            df_curve=convert_dataframe_to_localtime(df_curve)
            cprices=[]
            cpricedet=[]
            for p in period_prices:
                cprices.append({'ticker':p['period_tag'],
                                'mean_price': p['mean_price'],
                                'contract_price':p['contract_price']})
                df_pricing = pd.DataFrame(data=eval(p['pricing_details']))
                df_pricing.index=df_pricing['period_from']
                df_pricing = convert_dataframe_to_localtime(df_pricing)
                cpricedet.append(df_pricing)
            return df_curve, cprices, cpricedet
        else:
            print(error_msg)
        return None, error_msg, []




