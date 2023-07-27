import logging
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from datetime import timezone, datetime, date
import json
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from json import JSONEncoder
from dataclasses import dataclass
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from datetime import datetime, timedelta
import pytz
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
import pendulum
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum, AssetForecastAdjustDenomEnum
from energydeskapi.assets.assets_api import AssetsApi
logger = logging.getLogger(__name__)


class TimeSeriesEntry:
    def __init__(self, ts_datetime_utc, value, loczone="Europe/Oslo"):
        self.value=value
        self.timestamp=ts_datetime_utc.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        #d_aware = pytz.UTC.localize(ts_datetime_utc)
        d_loc = ts_datetime_utc.astimezone(pytz.timezone(loczone))   #For correct date
        self.localdate=d_loc.strftime('%Y-%m-%d')
    def get_dict(self):
        dict = {'datetime': self.timestamp, 'date': self.localdate, 'value':self.value}
        return dict



class TimeSeries:
    def __init__(self,asset_id, tseries_type=TimeSeriesTypesEnum.FORECASTS, unit="MWh"):
        self.timeseries_type=tseries_type
        self.unit=unit
        self.asset_id=asset_id
        self.timeseries_list=[]

    def get_dict(self):

        dict = {'asset_id': self.asset_id, 'unit': self.unit, 'timeseries_type':self.timeseries_type.name}
        dictlist=[]
        for el in self.timeseries_list:
            dictlist.append(el.get_dict())
        dict['timeseries']=dictlist
        return dict



class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00")
        except:
            pass
    return json_dict

@dataclass
class TimeSeriesAdjustment:
    pk : int
    description : str
    adjustment_type_pk : int
    value : str
    value_denomination: int
    value2 : str
    value2_denomination: int
    period_from :datetime
    period_until: datetime
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
    def get_dict(self, api_conn):
        dict = {'pk':self.pk}
        if self.description is not None: dict['description'] = self.description
        if self.adjustment_type_pk is not None: dict['adjustment_type'] = AssetDataApi.get_timeseries_adjustment_type_url(api_conn,self.adjustment_type_pk)
        print(self.value_denomination, self.value2_denomination)
        if self.value_denomination is not None: dict['value_denomination'] = AssetDataApi.get_timeseries_adjustment_denomination_type_url(api_conn,int(self.value_denomination))
        if self.value is not None: dict['value'] = self.value
        if self.value2 is not None and self.value2!="" and len(self.value2)>0:
            dict['value2'] = self.value2
            print("Seeting",self.value2)
            if self.value2_denomination is not None: dict['value2_denomination'] = AssetDataApi.get_timeseries_adjustment_denomination_type_url(api_conn,int(self.value2_denomination))

        if self.period_from is not None and self.period_from!="":
            dict['period_from'] = self.period_from if type(self.period_from) == str else self.period_from.strftime("%Y-%m-%d")
        if self.period_until is not None and self.period_until!="":
            dict['period_until'] = self.period_until if type(self.period_until)==str else self.period_until.strftime("%Y-%m-%d")
        #dict['denomination']=self.value_denomination
        #if self.value2_denomination is not None:
        #    dict['denomination2'] = self.value2_denomination
        print(dict)
        return dict
@dataclass
class TimeSeriesAdjustments:
    pk : int
    asset_pk : int
    time_series_type_pk: int
    is_active_for_asset: bool
    adjustments : list
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)
    def get_dict(self,api_conn):
        dict = {}
        dict['pk']=self.pk
        if self.time_series_type_pk is not None: dict['time_series_type'] = AssetDataApi.get_timeseries_type_url(api_conn,self.time_series_type_pk)
        if self.asset_pk is not None: dict['asset'] = AssetsApi.get_asset_url(api_conn,self.asset_pk)
        dict_list=[]
        for el in self.adjustments:
            dict_list.append(el.get_dict(api_conn))
        dict['adjustments']=dict_list
        if self.is_active_for_asset is not None: dict['is_active_for_asset'] = self.is_active_for_asset
        return dict

def demo_data(api_conn):
    curr=datetime.today().strftime(("%Y-%m-%d"))
    next = (datetime.today() + timedelta(days=1000)).strftime(("%Y-%m-%d"))
    explist=[]
    ta=TimeSeriesAdjustment(0,"Base Rebate",AssetForecastAdjustEnum.PERCENTAGE.value, "Prc", 0.94,0,None,None )
    explist.append(ta)
    ta=TimeSeriesAdjustment(0,"High tax Calc",AssetForecastAdjustEnum.PERCENTAGE.value, "Prc", 0.2,0,curr,next )
    explist.append(ta)
    tas=TimeSeriesAdjustments(0,5,1,True, explist)

    return tas.get_dict(api_conn)

class AssetDataApi:
    """ Class for asset data

    """

    @staticmethod
    def get_timeseries_adjustments(api_connection,  parameters={}):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: dictionary of filters to query
        :type parameters: dict, required
        """

        json_res = api_connection.exec_get_url('/api/assetdata/timeseriesadjustments/', parameters)
        if json_res is not None:
            return json_res
        return None
        #return TimeSeriesAdjustments(0,5,1,True, []).get_dict(api_connection)


    @staticmethod
    def upsert_timeseries_adjustments(api_connection,  adjustments):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: dictionary of filters to query
        :type parameters: dict, required
        """
        print(adjustments.get_dict(api_connection))
        if adjustments.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/assetdata/timeseriesadjustments/' + str(adjustments.pk) + "/", adjustments.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/assetdata/timeseriesadjustments/', adjustments.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_timeseries_adjustment_types(api_connection,  parameters={}):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: dictionary of filters to query
        :type parameters: dict, required
        """
        atype_list=[(el.value, el.name) for el in AssetForecastAdjustEnum]
        return atype_list

    @staticmethod
    def get_timeseries_adjustment_denominations(api_connection,  parameters={}):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: dictionary of filters to query
        :type parameters: dict, required
        """
        atype_list=[(el.value, el.name) for el in AssetForecastAdjustDenomEnum]
        return atype_list


    @staticmethod
    def get_timeseries_adjustment_denomination_type_url(api_connection, denomination_type):
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """
        print("Demon type", denomination_type)
        # Will accept both integers of the actual enum type
        type_pk = denomination_type if isinstance(denomination_type, int) else denomination_type.value
        return api_connection.get_base_url() + '/api/assetdata/timeseriesdenominations/' + str(type_pk) + "/"

    @staticmethod
    def get_timeseries_adjustment_type_url(api_connection, adjustment_type):
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """
        # Will accept both integers of the actual enum type
        type_pk = adjustment_type if isinstance(adjustment_type, int) else adjustment_type.value
        return api_connection.get_base_url() + '/api/assetdata/timeseriesadjustmenttypes/' + str(type_pk) + "/"

    @staticmethod
    def get_timeseries_type_url(api_connection, timeseries_type):
        """
        """
        # Will accept both integers of the actual enum type
        type_pk = timeseries_type if isinstance(timeseries_type, int) else timeseries_type.value
        return api_connection.get_base_url() + '/api/assetdata/timeseriestypes/' + str(type_pk) + "/"

    @staticmethod
    def get_timeseries_type_url(api_connection, ts_type):
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """
        # Will accept both integers of the actual enum type
        type_pk = ts_type if isinstance(ts_type, int) else ts_type.value
        return api_connection.get_base_url() + '/api/assetdata/timeseriestypes/' + str(type_pk) + "/"

    @staticmethod
    def get_forecast_adjustment(api_connection, assets):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param assets: personal key of asset(s) in asset group
        :type assets: str, required
        """
        assets_list=[]
        for key in assets:
            asset=AssetsApi.get_asset_by_key(api_connection, key)
            if asset is not None:
                assets_list.append({"pk":asset['pk'], "asset_id":asset['asset_id']})
        payload={
            "assets":assets_list,
            "datatype":"FORECAST"

        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/assetdata/query-summed-timeseries/', payload)
        return json_res

    @staticmethod
    def get_latest_forecast(api_connection, parameters={}):
        logger.info("Retrieve previously stored forecasts")

        json_res = api_connection.exec_get_url('/api/assetdata/timeseriesdata/latest/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def upsert_timeseries(api_connection, asset_pk, timeseries_data, timeseries_type=TimeSeriesTypesEnum.FORECASTS):
        logger.info("Upload and merge timeseries")
        payload={
            'asset':AssetsApi.get_asset_url(api_connection, asset_pk),
            'time_series_type':AssetDataApi.get_timeseries_type_url(api_connection,timeseries_type),
            #'data':timeseries_data,
            'last_updated':str(pendulum.now('Europe/Oslo')),
            'update_from_timestamp': str(pendulum.now('Europe/Oslo')),
        }
        print(payload)
        return None,None,None,None
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/assetdata/timeseriesdata/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def upload_timeseries(api_connection,timeseries_data):
        logger.info("Upload and merge timeseries")

        #json_res = api_connection.exec('/api/assetdata/upload-timeseries/', timeseries_data.get_dict())
        payload=timeseries_data.get_dict()
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/assetdata/upload-timeseries/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_assetgroup_forecast(api_connection, parameters={}):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param assets: personal key of asset(s) in asset group
        :type assets: str, required
        """

        json_res = api_connection.exec_get_url('/api/assetdata/summedtimeseriesdata/', parameters)
        if json_res is not None:
            return json_res
        return None


    @staticmethod
    def get_assetgroup_timeseries(api_connection,assets, timseries_types=TimeSeriesTypesEnum.FORECASTS, reso=PeriodResolutionEnum.MONTHLY):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param assets: personal key of asset(s) in asset group
        :type assets: str, required
        """
        parameters={
            "asset_id_in":assets,
            "resolution": reso.value,
            "timeseries_type":timseries_types.name
        }
        json_res = api_connection.exec_get_url('/api/assetdata/summedtimeseriesdata/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_assetgroup_forecast_df(api_connection, assets, reso=PeriodResolutionEnum.MONTHLY):
        """Fetches forecast for asset group and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param assets: personal key of asset(s) in asset group
        :type assets: str, required
        """

        params={"asset_id_in":assets, "resolution":reso.value}
        json_res=AssetDataApi.get_assetgroup_forecast(api_connection, params)
        if json_res is not None and len(json_res)>0:
            df = pd.DataFrame(data=json.loads(json_res))
            df.index = df['timestamp']
            df.index = pd.to_datetime(df.index)
            df = df.tz_convert("Europe/Oslo")
            df['timestamp'] = df.index
            return df
        return None

