import logging
import pandas as pd
from energydeskapi.assets.assets_api import AssetsApi
logger = logging.getLogger(__name__)

#fields = ['pk', 'asset_id', 'extern_asset_id', 'description', 'asset_type', 'grid_connection', 'power_supplier',
 #         'asset_owner', 'asset_manager', 'meter_id', 'sub_meter_id', 'vendor', 'is_active']



class AssetDataApi:
    """ Class for asset data

    """


    @staticmethod
    def get_assetgroup_forecast(api_connection, assets):
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

