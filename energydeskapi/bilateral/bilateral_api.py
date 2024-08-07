import logging
import pandas as pd
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from datetime import datetime, timedelta, timezone, date
from dateutil import parser
from energydeskapi.bilateral.rates_config import RatesConfig
import pytz
from energydeskapi.types.market_enum_types import ProfileTypeEnum
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
        self.weekday_cutoff = 0
        self.date_cutoff_override = None
        self.is_active_for_area = True
        self.basic_curve_model = None
        self.yearly_epad_reduction = {'yearly_values':[]}
        # Each point in list list above should be of format
        # {"from_date": "2026-01-01", "value": 0.9}  90%
        # Each point in list lists below should be of format
        # {"from_date": "2026-01-01", "currency_code": "NOK", "value": -50}
        self.spread_adjustment_epad = {'yearly_values':[]}
        self.spread_adjustment_sys = {'yearly_values':[]}

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.price_area is not None: dict['price_area'] = self.price_area
        if self.price_area is not None: dict['price_area'] = self.price_area
        if self.date_cutoff_override is not None: dict['date_cutoff_override'] = self.date_cutoff_override
        if self.is_active_for_area is not None: dict['is_active_for_area'] = self.is_active_for_area
        if self.basic_curve_model is not None: dict['basic_curve_model'] = self.basic_curve_model
        dict['weekday_cutoff'] = self.weekday_cutoff
        dict['yearly_epad_reduction'] = self.yearly_epad_reduction
        dict['spread_adjustment_epad'] = self.spread_adjustment_epad
        dict['spread_adjustment_sys'] = self.spread_adjustment_sys
        return dict


class RatesConfigurations:
    def __init__(self, wacc, discount_factor=0):
        self.pk = 0
        self.description="Default Rates"
        self.rates_data=RatesConfig(wacc, discount_factor)
        self.rates_application = 1

    def get_dict(self,api_conn):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        dict['wacc'] = self.rates_data.wacc
        dict['inflation'] = self.rates_data.inflation
        dict['discount_factor'] = self.rates_data.discount_factor
        dict['company_tax_rate'] = self.rates_data.company_tax_rate
        dict['land_value_tax_rate'] = self.rates_data.land_value_tax_rate
        dict['high_price_tax_rate'] = self.rates_data.high_price_tax_rate
        dict['high_price_tax_trigger'] = self.rates_data.high_price_tax_trigger
        dict['high_price_tax_start_date'] = self.rates_data.high_price_tax_start_date.strftime("%Y-%m-%d")
        dict['high_price_tax_end_date'] = self.rates_data.high_price_tax_end_date.strftime("%Y-%m-%d")
        if self.rates_application != 0: dict['rates_application'] = BilateralApi.get_rates_application_url(api_conn,self.rates_application)

        return dict






class BilateralApi:
    """Class for managing pricing of bilateral contracts

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
        print("Calculating deliveries with resolution ", resolution)
        success, json_res, status_code, error_msg = BilateralApi.calculate_deliveries(api_connection ,period_from, period_until, resolution, area_filter, counterpart_filter)
        if success==False:
            return success, None, None, status_code, error_msg

        deliveries=json_res['bilateral_deliveries']
        if len(deliveries)==0:
            return True, None, None, status_code, error_msg
        df_deliveries = pd.DataFrame(data=eval(deliveries))
        df_deliveries.index = df_deliveries['period_from']
        if 'bilateral_trades' in json_res and len(json_res['bilateral_trades'])>0:
            trades = json_res['bilateral_trades']
            df_trades = pd.DataFrame(data=eval(trades))
        else:
            df_trades=None

        return True, df_deliveries,df_trades, status_code, error_msg


    @staticmethod
    def calculate_contracted_capacity(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value, groupby=None):
        qry_payload = {
                "period_from": period_from,
                "period_until": period_until,
                "resolution":resolution,
                "groupby":groupby
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractedcapacity/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_contracted_capacity_df(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value, groupby=None):
        print("Calculating deliveries with resolution ", resolution)
        success, json_res, status_code, error_msg = BilateralApi.calculate_contracted_capacity(api_connection ,period_from, period_until, resolution, groupby)
        if success==False:
            return success, None, None, status_code, error_msg

        deliveries=json_res['bilateral_deliveries']
        if len(deliveries)==0:
            return True, None, None, status_code, error_msg
        df_deliveries = pd.DataFrame(data=eval(deliveries))
        df_deliveries.index = df_deliveries['period_from']
        if 'bilateral_trades' in json_res and len(json_res['bilateral_trades'])>0:
            trades = json_res['bilateral_trades']
            df_trades = pd.DataFrame(data=eval(trades))
        else:
            df_trades=None

        return True, df_deliveries,df_trades, status_code, error_msg

    @staticmethod
    def get_bilateral_trades(api_connection, period_from, period_until):
        qry_payload = {
            "period_from": period_from,
            "period_until": period_until,
        }

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/trades/',
                                                                                 qry_payload)
        print(success)
        if success is False:
            return success, None, status_code, error_msg
        if len(json_res['bilateral_trades']) == 0:
            return success, None, status_code, error_msg
        try:
            internjson=json.loads(json_res['bilateral_trades'])
            df_trades = pd.DataFrame(data=internjson)
            return success, df_trades, status_code, error_msg
        except:
            return False, None, status_code, "Problems reading the list of trades from server"

    @staticmethod
    def get_bilateral_trades_for_externals(api_connection, period_from, period_until):
        qry_payload = {
            "period_from": period_from,
            "period_until": period_until,
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/trades/external/',
                                                                                 qry_payload)
        print(success)
        if success is False:
            return success, None, status_code, error_msg
        if len(json_res['bilateral_trades']) == 0:
            return success, None, status_code, error_msg
        try:
            internjson=json.loads(json_res['bilateral_trades'])
            df_trades = pd.DataFrame(data=internjson)
            return success, df_trades, status_code, error_msg
        except:
            return False, None, status_code, "Problems reading the list of trades from server"


    @staticmethod
    def get_avaiable_fixprice_periods(api_connection):
        """Fetches pricing configurations

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching current open fixprice periods")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/contractpricer/allowedperiods/')
        return json_res

    @staticmethod
    def get_contract_doc(api_connection, external_id):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query contract_doc")
        json_res = api_connection.exec_get_url('/api/bilateral/contractdoc/', parameters={'external_id': external_id})
        return json_res

    @staticmethod
    def get_capacity_contract_doc(api_connection, external_id):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query contract_doc")
        url = '/api/bilateral/capacity/contractdoc/?external_id=' + external_id
        json_res = api_connection.exec_get_url(url)
        return json_res

    @staticmethod
    def preview_capacity_contract_doc(api_connection, payload):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query contract_doc")
        url = '/api/bilateral/capacity/previewcontractdoc/'
        json_res = api_connection.exec_post_url(url, payload)
        return json_res

    @staticmethod
    def get_contract_profile(api_connection, contract_id, resolution="Monthly"):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query contract_doc")
        params= {"id":contract_id, "resolution":resolution}
        url = '/api/portfoliomanager/contractprofile/'
        json_res = api_connection.exec_get_url(url, params)
        if type(json_res)==str:
            df=pd.DataFrame(data=json.loads(json_res))
        else:
            df = pd.DataFrame(data=json_res)
        if len(df)==0:
            return None
        df.index=df.period_from
        df=df[['netpos','buypos','sellpos','netvol','buyvol','sellvol', 'hours']]
        df.index=pd.to_datetime(df.index)
        df=df.tz_convert("Europe/Oslo")
        return df


    @staticmethod
    def get_capacity_allocation(api_connection, periods, substation_profile):
        dict_periods=[]
        for p in periods:
            dict_periods.append({
            "period_tag": p[0],
            "contract_date_from":p[1],
            "contract_date_until": p[2],
            })
        qry_payload = {
                "substation_profile":substation_profile,
                "periods":dict_periods,
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/capacity/allocation/', qry_payload)
        return success, json_res, status_code, error_msg
    @staticmethod
    def upsert_capacity_allocation(api_connection, periods, substation_profile, capacity_map):
        dict_periods=[]
        for p in periods:
            dict_periods.append({
            "period_tag": p[0],
            "contract_date_from":p[1],
            "contract_date_until": p[2],
            })
        qry_payload = {
                "capacity_map": capacity_map,
                "substation_profile":substation_profile,
                "periods":dict_periods,
        }

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/capacity/allocation/', qry_payload)
        return success, json_res, status_code, error_msg
    @staticmethod
    def calculate_capacity_price(api_connection, periods, substation_profile, current_price, activation_price, currency_code="NOK"):
        dict_periods=[]
        for p in periods:
            dict_periods.append({
            "period_tag": p[0],
            "contract_date_from":p[1],
            "contract_date_until": p[2],
            })
        qry_payload = {
                "currency_code": currency_code,
                "substation_profile":substation_profile,
                "periods":dict_periods,
                "current_price": current_price,
                "activation_price":activation_price
        }

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/capacity/', qry_payload)
        return success, json_res, status_code, error_msg
    @staticmethod
    def calculate_contract_price(api_connection ,periods, price_area, currency_code,
                                 curve_model, wacc=0.06, inflation=0,profile_type=ProfileTypeEnum.BASELOAD,
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
                "profile_type": profile_type.name,
                "monthly_profile":monthly_profile,
                "weekday_profile": weekday_profile,
                "daily_profile": hours
        }

        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/internal/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_contract_price_df(api_connection, periods, price_area, currency_code,curve_model,
                                    wacc=0.06, inflation=0,profile_type=ProfileTypeEnum.BASELOAD,
                                    monthly_profile=get_baseload_months(),
                                    weekday_profile=get_baseload_weekdays(),
                                    hours=get_baseload_dailyhours()
                                    ):

        print(periods, price_area, currency_code, curve_model)
        success, json_res, status_code, error_msg=BilateralApi.calculate_contract_price(api_connection, periods, price_area,
                                                                                        currency_code, curve_model,
                                 wacc, inflation,profile_type, monthly_profile, weekday_profile, hours)
        if success and 'period_prices' in json_res:
            #print(json_res)
            period_prices = json_res['period_prices']
            curve=json_res['forward_curve']
            price_date = json_res['price_date']
            currency_date = json_res['currency_date']
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
            return price_date,currency_date, df_curve, cprices, cpricedet
        else:
            print("No prices returned")
            if success==False:
                print(error_msg)

        return None, None, None, "error_msg", []

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
        print("RETURNED CURVES CONFIGS", json_res)
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
            pricing_dict = pricing_conf.get_dict(api_connection)
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
                                yearly_epad_reduction,
                                spread_adjustment_sys, spread_adjustment_epad, curve_date=datetime.today()):
        logger.info("Adjusting curve from parameters")
        payload={
            'price_area':price_area,
            'yearly_epad_reduction':yearly_epad_reduction,
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
            df_yearly = df_yearly.rename(columns={"hourly_consumption": "yearly_volume", "count": "hours"})

            f2list = [pd.Grouper(level='datetime', freq="MS")]
            df_monthly = df.groupby(f2list).agg({'hourly_consumption': sum, 'count': sum})
            df_monthly = df_monthly.rename(columns={"hourly_consumption": "monthly_volume", "count": "hours"})


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


    @staticmethod
    def get_rates_application_url(api_connection, rates_application_enum):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param quantity_type_enum: type of contract
        :type quantity_type_enum: str, required
        """
        type_pk = rates_application_enum if isinstance(rates_application_enum, int) else rates_application_enum.value
        return api_connection.get_base_url() + '/api/bilateral/ratesapplication/' + str(type_pk) + "/"