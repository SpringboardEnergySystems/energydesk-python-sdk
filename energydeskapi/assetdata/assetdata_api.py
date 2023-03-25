import logging
import pandas as pd
from datetime import datetime, timedelta

from datetime import datetime, timedelta
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum
from energydeskapi.assets.assets_api import AssetsApi
logger = logging.getLogger(__name__)

class TimeSeriesAdjustment:
    def __init__(self):
        self.pk = 0
        self.description = None
        self.adjustment_type_pk=None
        self.denomination_type_pk=None
        self.value = None
        self.value2 = None
        self.period_from = None
        self.period_until = None
    def get_dict(self, api_conn):
        dict = {}
        if self.description is not None: dict['description'] = self.description
        if self.adjustment_type_pk is not None: dict['adjustment_type'] = AssetDataApi.get_timeseries_adjustment_type_url(api_conn,self.adjustment_type_pk)
        if self.denomination_type_pk is not None: dict['denomination'] = "test"#AssetDataApi.get_timeseries_adjustment_type_url(api_conn,self.denomination_type_pk)
        if self.value is not None: dict['value'] = self.value
        if self.value2 is not None: dict['value2'] = self.value2
        if self.period_from is not None: dict['period_from'] = self.period_from
        if self.period_until is not None: dict['period_until'] = self.period_until
        return dict

class TimeSeriesAdjustments:
    def __init__(self):
        self.pk = 0
        self.asset_pk=None
        self.adjustments = []
        self.time_series_type_pk=None
        self.is_active_for_asset = True
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
    tss = TimeSeriesAdjustments()
    tss.is_active_for_asset=True
    tss.asset_pk=AssetsApi.get_asset_url(api_conn,5)

    ts=TimeSeriesAdjustment()
    ts.description="Base rebate"
    ts.value=0.95
    ts.adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value#AssetDataApi.get_timeseries_adjustment_type_url(api_conn, AssetForecastAdjustEnum.PERCENTAGE.value)
    ts.denomination_type_pk=1#AssetDataApi.get_timeseries_adjustment_denomination_type_url(api_conn, 1)
    tss.adjustments.append(ts)


    ts=TimeSeriesAdjustment()
    ts.description = "High tax rebate"
    ts.value=0.30
    ts.period_from=curr
    ts.period_until=next
    ts.adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value#AssetDataApi.get_timeseries_adjustment_type_url(api_conn, AssetForecastAdjustEnum.PERCENTAGE.value)
    ts.denomination_type_pk=1#AssetDataApi.get_timeseries_adjustment_denomination_type_url(api_conn, 1)
    tss.adjustments.append(ts)

    ts=TimeSeriesAdjustment()
    ts.description = "Option cust rebate"
    ts.value=0.70
    ts.adjustment_type_pk=AssetForecastAdjustEnum.EUROP_OPTION.value#AssetDataApi.get_timeseries_adjustment_type_url(api_conn, AssetForecastAdjustEnum.EUROP_OPTION.value)
    ts.denomination_type_pk=2#AssetDataApi.get_timeseries_adjustment_denomination_type_url(api_conn, 2)
    tss.adjustments.append(ts)

    return tss.get_dict()

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
        return demo_data(api_connection)


    @staticmethod
    def upsert_timeseries_adjustments(api_connection,  adjustments):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: dictionary of filters to query
        :type parameters: dict, required
        """

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
    def get_timeseries_adjustment_denomination_types(api_connection,  parameters={}):
        """Fetches forecast for asset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param parameters: dictionary of filters to query
        :type parameters: dict, required
        """
        denoms=[(1,'%'),(2,'NOK')]
        return denoms


    @staticmethod
    def get_timeseries_adjustment_denomination_type_url(api_connection, denomination_type):
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """
        # Will accept both integers of the actual enum type
        type_pk = denomination_type if isinstance(denomination_type, int) else denomination_type.value
        return api_connection.get_base_url() + '/api/assetdata/timeseriesadjustmenttypes/' + str(type_pk) + "/"

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
    def get_assetgroup_forecast_df(api_connection, assets):
        """Fetches forecast for asset group and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param assets: personal key of asset(s) in asset group
        :type assets: str, required
        """
        json_res=AssetDataApi.get_assetgroup_forecast(api_connection, assets)
        if json_res is not None and len(json_res)>0:
            df = pd.DataFrame(data=eval(json_res))
            df['date']= pd.to_datetime(df['date'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.index=df['timestamp']
            return df
        return None

