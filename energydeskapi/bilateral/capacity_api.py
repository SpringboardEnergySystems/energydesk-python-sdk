import logging
import pandas as pd
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from datetime import datetime, timedelta, timezone, date
from dateutil import parser
from energydeskapi.bilateral.rates_config import RatesConfig
import pytz
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.market_enum_types import ProfileTypeEnum
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.types.market_enum_types import ProfileTypeEnum
from energydeskapi.profiles.profiles_api import ProfilesApi
from energydeskapi.profiles.profiles import GenericProfile
import json
from energydeskapi.sdk.datetime_utils import convert_datime_to_locstr
from energydeskapi.marketdata.products_api import ProductsApi
from dateutil import relativedelta
from energydeskapi.sdk.pandas_utils import convert_dataframe_to_localtime
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
from energydeskapi.assets.assets_api import AssetsApi
logger = logging.getLogger(__name__)
class CapacityProfile():
  def __init__(self):
    self.pk = 0
    self.grid_component = None
    self.requested_profile = None
    self.period_from = None
    self.period_until = None

  def get_dict(self, api_conn):
    dict = {}
    dict['pk'] = self.pk
    if self.grid_component is not None: dict['grid_component'] = AssetsApi.get_asset_url(api_conn, self.grid_component)
    if self.requested_profile is not None: dict['requested_profile'] = self.requested_profile
    if self.period_from is not None: dict['period_from'] = self.period_from
    if self.period_until is not None: dict['licenced_until'] = self.period_until
    return dict

class CapacityApi:

    @staticmethod
    def get_capacity_profile(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/request/calculated/', parameters)
        if json_res is not None:
          return json_res
        return None

    @staticmethod
    def get_capacity_request(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/request/', parameters)
        if json_res is not None:
          return json_res
        return None


    @staticmethod
    def upsert_capacity_request(api_connection, capacity_profile):
      if capacity_profile.pk > 0:
          success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
              '/api/bilateral/capacity/request/' + str(capacity_profile.pk) + "/", capacity_profile.get_dict(api_connection))
      else:
          success, returned_data, status_code, error_msg = api_connection.exec_post_url(
              '/api/bilateral/capacity/request/', capacity_profile.get_dict(api_connection))
      return success, returned_data, status_code, error_msg

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
    def add_order_from_priceoffer_id(api_connection ,priceoffer_id, buy_or_sell, quantity,
                                     quantity_type=QuantityTypeEnum.VOLUME_YEARLY.name,
                                     quantity_unit=QuantityUnitEnum.KW.name):
        """Add order with reference to a price quote
        """
        logger.info("Adding order")

        qry_payload = {
                "buy_or_sell": buy_or_sell,
                "priceoffer_id": priceoffer_id,
                "quantity":quantity,
                "quantity_type":quantity_type,
                "quantity_unit": quantity_unit
        }

        logger.info(str(qry_payload))
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorderbypriceoffer/', qry_payload)
        return success, json_res, status_code, error_msg
