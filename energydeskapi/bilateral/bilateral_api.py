import logging
import pandas as pd

from datetime import datetime, timedelta, timezone
import pytz
from dateutil import relativedelta

logger = logging.getLogger(__name__)

class BilateralApi:
    """Class for price curves

    """

    @staticmethod
    def calculate_contract_price(api_connection ,periods, price_area, currency_code, curve_model, contract_type="BASELOAD", monthly_profile=[], weekday_profile=[]):
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
                "contract_type":contract_type,
                "periods":dict_periods,
                "monthly_profile":monthly_profile,
                "weekday_profile": weekday_profile
        }

        #print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_contract_price_df(api_connection, periods, price_area, currency_code, curve_model,
                                 contract_type="BASELOAD", monthly_profile=[], weekday_profile=[]):
        success, json_res, status_code, error_msg=BilateralApi.calculate_contract_price(api_connection, periods, price_area, currency_code, curve_model,
                                 contract_type, monthly_profile, weekday_profile)
        if success:
            period_prices = json_res['period_prices']
            df_curve = pd.DataFrame(data=eval(json_res['forward_curve']))
            df_curve.index=df_curve['date']
            norzone = pytz.timezone('Europe/Oslo')
            df_curve.index = pd.to_datetime(df_curve.index)
            df_curve.index = df_curve.index.tz_convert(tz=norzone)
            df_curve['date'] = pd.to_datetime(df_curve['date'])
            df_curve['date'] = df_curve['date'].dt.tz_convert(tz=norzone)
            df_curve['period_from'] = pd.to_datetime(df_curve['period_from'])
            df_curve['period_from'] = df_curve['period_from'].dt.tz_convert(tz=norzone)
            df_curve['period_until'] = pd.to_datetime(df_curve['period_until'])
            df_curve['period_until'] = df_curve['period_until'].dt.tz_convert(tz=norzone)
            cprices=[]
            cpricedet=[]
            for p in period_prices:
                cprices.append(p['contract_price'])
                df_pricing = pd.DataFrame(data=eval(p['pricing_details']))
                df_pricing['period_from'] = pd.to_datetime(df_pricing['period_from'])
                df_pricing['period_from'] = df_pricing['period_from'].dt.tz_convert(tz=norzone)
                df_pricing['period_until'] = pd.to_datetime(df_pricing['period_until'])
                df_pricing['period_until'] = df_pricing['period_until'].dt.tz_convert(tz=norzone)
                df_pricing.index=df_pricing['period_from']
                cpricedet.append(df_pricing)
            return df_curve, cprices, cpricedet
        else:
            print(error_msg)
        return None, [], []




