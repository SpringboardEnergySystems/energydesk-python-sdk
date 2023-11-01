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
class CapacityApi:

  @staticmethod
  def get_capacity_profile(api_connection, parameters={}):
    json_res = api_connection.exec_get_url('/api/bilateral/capacity/request/calculated/', parameters)
    if json_res is not None:
      return json_res
    return None