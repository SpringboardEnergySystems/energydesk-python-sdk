import logging
import pandas as pd
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from datetime import datetime, timedelta, timezone, date
from dateutil import parser
import pytz
from energydeskapi.profiles.profiles_api import ProfilesApi
from energydeskapi.profiles.profiles import GenericProfile
import json
from energydeskapi.sdk.datetime_utils import convert_datime_to_locstr
from energydeskapi.marketdata.products_api import ProductsApi
from dateutil import relativedelta
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
logger = logging.getLogger(__name__)

class CurvesConfigurations:
    def __init__(self):
        self.pk = 0
        self.description=None
        self.price_area = None
        self.basic_curve_model = None
        self.yearly_epad_converging = []
        self.spread_adjustment_epad = []
        self.spread_adjustment_sys = []

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.price_area is not None: dict['price_area'] = self.price_area
        if self.basic_curve_model is not None: dict['basic_curve_model'] = self.basic_curve_model
        if len(self.yearly_epad_converging)>0: dict['yearly_epad_converging'] = self.yearly_epad_converging
        if len(self.spread_adjustment_epad)> 0: dict['spread_adjustment_epad'] = self.spread_adjustment_epad
        if len(self.spread_adjustment_sys)>0: dict['spread_adjustment_sys'] = self.spread_adjustment_sys
        return dict


class RatesConfigurations:
    def __init__(self):
        self.pk = 0
        self.description=None
        self.wacc = 0
        self.inflation = 0
        self.discount_factor = 0
        self.company_tax_rate=0
        self.land_value_tax_rate=0
        self.high_price_tax_rate=0
        self.high_price_tax_trigger=0
        self.high_price_tax_start_date=date(2022,1,1)
        self.high_price_tax_end_date = date(2025, 1, 1)
        self.rates_application = 1

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.wacc != 0: dict['wacc'] = self.wacc
        if self.inflation != 0: dict['inflation'] = self.inflation
        if self.discount_factor != 0: dict['discount_factor'] = self.discount_factor
        if self.company_tax_rate != 0: dict['company_tax_rate'] = self.company_tax_rate
        if self.land_value_tax_rate != 0: dict['land_value_tax_rate'] = self.land_value_tax_rate
        if self.high_price_tax_rate != 0: dict['high_price_tax_rate'] = self.high_price_tax_rate
        if self.high_price_tax_start_date != 0: dict['high_price_tax_start_date'] = self.high_price_tax_start_date.strftime("%Y-%m-%d")
        if self.high_price_tax_end_date != 0: dict['high_price_tax_end_date'] = self.high_price_tax_end_date.strftime("%Y-%m-%d")
        if self.rates_application != 0: dict['rates_application'] = self.rates_application

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
        if success and 'period_prices' in json_res:
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
            print("No prices returned")
            if success==False:
                print(error_msg)

        return None, "error_msg", []

    @staticmethod
    def get_rates_configurations(api_connection):
        """Fetches pricing configurations

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching pricing configurations")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/ratesconfigurations/')
        return json_res

    @staticmethod
    def get_curve_configurations(api_connection):
        """Fetches pricing configurations

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching curve configurations")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/curvesconfigurations/')
        return json_res

    @staticmethod
    def get_rates_configuration_by_pk(api_connection, pk):
        """Fetches pricing configuration from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching pricing configuration")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/ratesconfigurations/' + str(pk) + '/')
        return json_res

    @staticmethod
    def get_curve_configuration_by_pk(api_connection, pk):
        """Fetches pricing configuration from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching curve configuration")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/curvesconfigurations/' + str(pk) + '/')
        return json_res

    @staticmethod
    def upsert_rates_configuration(api_connection, pricing_conf):
        logger.info("Registering pricing configuration")
        if type(pricing_conf) is dict:
            pk = pricing_conf['pk']
            pricing_dict = pricing_conf
        else:
            pk = pricing_conf.pk
            pricing_dict = pricing_conf.get_dict()
        print(pricing_dict)
        if pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/bilateral/ratesconfigurations/' + str(pk) + "/", pricing_dict)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/bilateral/ratesconfigurations/', pricing_dict)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def upsert_curve_configuration(api_connection, curve_conf):
        logger.info("Registering pricing configuration")
        if type(curve_conf) is dict:
            pk = curve_conf['pk']
            pricing_dict = curve_conf
        else:
            pk = curve_conf.pk
            pricing_dict = curve_conf.get_dict()
        print(pricing_dict)
        if pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/bilateral/curvesconfigurations/' + str(pk) + "/", pricing_dict)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/bilateral/curvesconfigurations/', pricing_dict)
        return success, returned_data, status_code, error_msg


    @staticmethod
    def generate_adjusted_curve_from_config(api_connection, pricing_config_pk, curve_date=datetime.today()):
        logger.info("Adjusting curve")
        payload={
            'pricing_config_pk':pricing_config_pk,
            'curve_date':curve_date.strftime(("%Y-%m-%d"))
        }
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/bilateral/curveadjustment/fromconfig/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def generate_adjusted_curve(api_connection, price_area,
                                yearly_epad_converging, spread_adjustment_epad,
                                spread_adjustment_sys, curve_date=datetime.today()):
        logger.info("Adjusting curve from parameters")
        payload={
            'price_area':price_area,
            'yearly_epad_converging':yearly_epad_converging,
            'spread_adjustment_epad':spread_adjustment_epad,
            'spread_adjustment_sys':spread_adjustment_sys,
            'curve_date':curve_date.strftime(("%Y-%m-%d"))
        }
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/bilateral/curveadjustment/', payload)
        return success, returned_data, status_code, error_msg



    # Loads a relative profile with delivery period, applied with a yearly volume
    @staticmethod
    def load_profiled_volume(api_connection, product_code, yearly_volume, include_hourly_series=False):
        """Loads a relative profile with delivery period, applied with a yearly volume

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        res = ProductsApi.get_commodity_definitions(api_connection, {"product_code": product_code})
        cr = res['results']
        if len(cr) == 1:
            print("Loaded commodity profile")
            dprof = GenericProfile.from_dict(cr[0]['commodity_profile'])
            print(cr[0])
            delivery_from = cr[0]['delivery_from']
            delivery_until = cr[0]['delivery_until']
            success, returned_data, status_code, error_msg = ProfilesApi.convert_relativeprofile_to_yearlyfactors(
                api_connection, delivery_from, delivery_until, dprof
            )
            if not success:
                return success, returned_data, status_code, error_msg

            df = pd.DataFrame(data=json.loads(returned_data))
            df.index = df['datetime']
            df.index = pd.to_datetime(df.index)
            df = df.tz_convert("Europe/Oslo")
            df['hourly_consumption'] = yearly_volume * df['monthly_factor'] * df['weekday_factor'] * df['hourly_factor']

            f2list = [pd.Grouper(level='datetime', freq="YS")]
            df_yearly = df.groupby(f2list).agg({'hourly_consumption': sum, 'count': sum})
            df_yearly = df_yearly.rename(columns={"hourly_consumption": "yearly_consumption", "count": "hours"})

            f2list = [pd.Grouper(level='datetime', freq="MS")]
            df_monthly = df.groupby(f2list).agg({'hourly_consumption': sum, 'count': sum})
            df_yearly = df_yearly.rename(columns={"hourly_consumption": "monthly_consumption", "count": "hours"})


            retval={
                "df_monthly":df_monthly,
                "df_yearly": df_yearly,
                "delivery_from": convert_datime_to_locstr(parser.isoparse(cr[0]['delivery_from'])),
                "delivery_until": convert_datime_to_locstr(parser.isoparse(cr[0]['delivery_until'])),
                "area": cr[0]['area']
            }
            if include_hourly_series:
                retval['df_hourly']=df
            return True, retval , 0, None
        else:
            return False, None, 0, "Profile with code " + product_code + " not found for period"


