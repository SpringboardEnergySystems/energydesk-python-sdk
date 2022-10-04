import requests
import json
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
        """Fetches asset from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_pk: personal key of asset
        :type asset_pk: str, required
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
        json_res = api_connection.exec_post_url('/api/assetdata/query-summed-timeseries/', payload)
        return json_res
    @staticmethod
    def get_assetgroup_forecast_df(api_connection, assets):
        json_res=AssetDataApi.get_assetgroup_forecast(api_connection, assets)
        if json_res is not None:
            df = pd.DataFrame(data=eval(json_res))
            return df
        return None

