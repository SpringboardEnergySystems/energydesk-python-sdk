from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
import pandas as pd
import pytz
import logging
from django.conf import settings
from datetime import datetime
from energydeskapi.assetdata.assetdata_api import AssetDataApi
from energydesk.api.api_manager import ApiManager
import json

logging.config.dictConfig(settings.LOG_CONFIG)
logger = logging.getLogger(__name__)

def load_multiasset_data(request, asset_pk_list=[], period_from:str="2024-01-01", period_until:str="2024-03-01", resolution= PeriodResolutionEnum.HOURLY.value):
    period_start = datetime.strptime(period_from, '%Y-%m-%d').replace(tzinfo=pytz.timezone("Europe/Oslo"))
    period_end = datetime.strptime(period_until, '%Y-%m-%d').replace(tzinfo=pytz.timezone("Europe/Oslo"))

    def load_asset_timeseries(asset_pk_list):
        params = {
            'id__in': [int(a) for a in asset_pk_list],
            'time_series_type__id': TimeSeriesTypesEnum.METERREADINGS.value,
            'resolution': resolution
        }
        print(params)
        jsdata = AssetDataApi.get_asset_timeseries(ApiManager.api_connection(request), params)
        if type(jsdata)==str:
            jsdata=json.loads(jsdata)
        df = pd.DataFrame(data=jsdata)
        if len(df)==0:
            return df
        df.index = df.timestamp
        df.index = pd.to_datetime(df.index)
        df = df.loc[(df.index >= period_start) & (df.index < period_end)]
        df = df.drop(columns=['date', 'timestamp'])
        return df

    df_metering = load_asset_timeseries(asset_pk_list)

    return df_metering