import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

#fields = ['pk', 'asset_id', 'extern_asset_id', 'description', 'asset_type', 'grid_connection', 'power_supplier',
 #         'asset_owner', 'asset_manager', 'meter_id', 'sub_meter_id', 'vendor', 'is_active']


class Asset:
    def __init__(self):
        self.pk=0
        self.asset_id=None
        self.extern_asset_id=None
        self.description=""
        self.asset_type=None
        self.grid_company=None
        self.power_supplier=None
        self.asset_owner=None
        self.asset_manager=None
        self.meter_id=""
        self.sub_meter_id=""
        self.vendor=None
        self.is_active=True



class AssetsApi:
    """ Class for assets

    """

    @staticmethod
    def get_asset_type_url(api_connection, asset_type_enum):
        return api_connection.get_base_url() + '/api/assets/assettype/' + str(asset_type_enum.value) + "/"

    @staticmethod
    def get_asset_type(api_connection, asset_type_enum):
        json_res = api_connection.exec_get_url('/api/assets/assettype/' + str(asset_type_enum.value)) + "/"
        if json_res is None:
            return None
        return json_res

    # This function returns a single price (avg) for the period requested
    @staticmethod
    def register_assets(api_connection, asset_list):
        """ Registers assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_list: list of assets
        :type asset_list: str, required
        """
        logger.info("Registering " + str(len(asset_list) )+ " assets")
        for asset in asset_list:
            payload={}
            if asset.asset_id is not None: payload['asset_id']=asset.asset_id
            if asset.extern_asset_id is not None: payload['extern_asset_id'] = asset.extern_asset_id
            if asset.description is not None: payload['description'] = asset.description
            if asset.asset_manager is not None: payload['asset_manager'] = asset.asset_manager
            json_res=api_connection.exec_post_url('/api/assets/asset/', payload)


    @staticmethod
    def get_asset_types(api_connection):
        """ Receives the type of assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assettype/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df


    @staticmethod
    def get_assets(api_connection):
        """ Receives the type of assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/asset/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_assets_ext(api_connection):
        """ Receives a list of assets with extended information

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assets_ext/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df
