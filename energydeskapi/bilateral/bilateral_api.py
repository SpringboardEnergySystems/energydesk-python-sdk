import logging
import pandas as pd
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from datetime import datetime, timedelta, timezone
import pytz
from dateutil import relativedelta
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
logger = logging.getLogger(__name__)

class PricingConfiguration:
    def __init__(self):
        self.pk = 0
        self.currency_code = None
        self.wacc = 0
        self.inflation = 0
        self.price_areas = None
        self.basic_curve_model = None
        self.yearly_epad_converging = 0
        self.spread_adjustment_epad = 0
        self.spread_adjustment_sys = 0
        self.counterpart_override = None
        self.is_default_config = True

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.currency_code is not None: dict['currency_code'] = self.currency_code
        if self.wacc != 0: dict['wacc'] = self.wacc
        if self.inflation != 0: dict['inflation'] = self.inflation
        if self.price_areas is not None: dict['price_areas'] = self.price_areas
        if self.basic_curve_model is not None: dict['basic_curve_model'] = self.basic_curve_model
        if self.yearly_epad_converging != 0: dict['yearly_epad_converging'] = self.yearly_epad_converging
        if self.spread_adjustment_epad != 0: dict['spread_adjustment_epad'] = self.spread_adjustment_epad
        if self.spread_adjustment_sys != 0: dict['spread_adjustment_sys'] = self.spread_adjustment_sys
        if self.counterpart_override is not None: dict['counterpart_override'] = self.counterpart_override
        if self.is_default_config is not False: dict['is_default_config'] = self.is_default_config
        return dict

class BilateralApi:
    """Class for price curves

    """

    @staticmethod
    def calculate_deliveries(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value, area_filter=None, counterpart_filter=None):
        qry_payload = {
                "period_from": period_from,
                "period_until": period_until,
                "resolution":resolution,
        }
        if area_filter is not None:
            qry_payload['area_filter']=area_filter
        if counterpart_filter is not None:
            qry_payload['counterpart_filter']=counterpart_filter
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/deliveries/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_deliveries_df(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value,  area_filter=None, counterpart_filter=None):

        success, json_res, status_code, error_msg = BilateralApi.calculate_deliveries(api_connection ,period_from, period_until, resolution, area_filter, counterpart_filter)
        if success==False:
            return success, None, None, status_code, error_msg

        deliveries=json_res['bilateral_deliveries']
        if len(deliveries)==0:
            return True, None, None, status_code, error_msg
        df_deliveries = pd.DataFrame(data=eval(deliveries))
        df_deliveries.index = df_deliveries['period_from']
        trades = json_res['bilateral_trades']
        df_trades = pd.DataFrame(data=eval(trades))
        #df_deliveries = convert_dataframe_to_localtime(df_deliveries)
        return True, df_deliveries,df_trades, status_code, error_msg

    @staticmethod
    def calculate_contract_price(api_connection ,periods, price_area, currency_code,
                                 curve_model, wacc=0.06, inflation=0,
                                 monthly_profile=get_baseload_months(),
                                 weekday_profile=get_baseload_weekdays(),
                                 hours=get_baseload_dailyhours()):
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
                "periods":dict_periods,
                "monthly_profile":monthly_profile,
                "weekday_profile": weekday_profile,
                "daily_profile": hours
        }

        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/internal/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_contract_price_df(api_connection, periods, price_area, currency_code,curve_model,
                                    wacc=0.06, inflation=0,
                                    monthly_profile=get_baseload_months(),
                                    weekday_profile=get_baseload_weekdays(),
                                    hours=get_baseload_dailyhours()
                                    ):

        print(periods, price_area, currency_code, curve_model)
        success, json_res, status_code, error_msg=BilateralApi.calculate_contract_price(api_connection, periods, price_area,
                                                                                        currency_code, curve_model,
                                 wacc, inflation, monthly_profile, weekday_profile, hours)
        if success:
            #print(json_res)
            period_prices = json_res['period_prices']
            curve=json_res['forward_curve']
            #print("PRICS", period_prices)
            #print("CURVE", curve)
            df_curve = pd.DataFrame(data=eval(curve))
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
            print("An error occured")
            pass#print(error_msg)
        return None, "error_msg", []

    @staticmethod
    def get_pricing_configurations(api_connection):
        """Fetches pricing configurations

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching pricing configurations")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/pricingconfiguration/')
        return json_res

    @staticmethod
    def get_pricing_configuration_by_pk(api_connection, pk):
        """Fetches pricing configuration from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching pricing configuration")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/pricingconfiguration/' + str(pk) + '/')
        return json_res

    @staticmethod
    def upsert_pricing_configuration(api_connection, pricing_conf):
        logger.info("Registering pricing configuration")
        if type(pricing_conf) is dict:
            pk = pricing_conf['key']
            pricing_dict = pricing_conf
        else:
            pk = pricing_conf.pk
            pricing_dict = pricing_conf.get_dict()
        if pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/bilateral/pricingconfiguration/' + str(pk) + "/", pricing_dict)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/bilateral/pricingconfiguration/', pricing_dict)
        return success, returned_data, status_code, error_msg



