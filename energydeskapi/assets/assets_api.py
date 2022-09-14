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
        self.is_main_meter=True
        self.location="0,0"
        self.is_active=True

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.asset_id is not None: dict['asset_id'] = self.asset_id
        if self.extern_asset_id is not None: dict['extern_asset_id'] = self.extern_asset_id
        if self.description is not None: dict['description'] = self.description
        if self.asset_type is not None: dict['asset_type'] = self.asset_type
        if self.grid_company is not None: dict['grid_connection'] = self.grid_company
        if self.power_supplier is not None: dict['power_supplier'] = self.power_supplier
        if self.asset_owner is not None: dict['asset_owner'] = self.asset_owner
        if self.asset_manager is not None: dict['asset_manager'] = self.asset_manager
        if self.meter_id is not None: dict['meter_id'] = self.meter_id
        if self.sub_meter_id is not None: dict['sub_meter_id'] = self.sub_meter_id
        if self.vendor is not None: dict['vendor'] = self.vendor
        if self.is_main_meter is not None: dict['is_main_meter'] = self.is_main_meter
        if self.is_active is not None: dict['is_active'] = self.is_active
        if self.location is not None: dict['location'] = self.location
        return dict


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
    def create_assets(api_connection, asset_list):
        """ Registers assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_list: list of assets
        :type asset_list: str, required
        """
        logger.info("Registering " + str(len(asset_list) )+ " assets")
        for asset in asset_list:
            payload=asset.get_dict()
            json_res=api_connection.exec_post_url('/api/assets/asset/', payload)
            if json_res is None:
                logger.error("Problems registering asset "  + asset.description)
            else:
                logger.info("Asset registered " + asset.description)

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
    def get_asset_url(api_connection, asset_pk):
        return api_connection.get_base_url() + '/api/assets/asset/' + str(asset_pk) + "/"

    @staticmethod
    def get_assets(api_connection):
        """ Receives the type of assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/asset/')
        print(json_res)
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

    @staticmethod
    def get_assetsbytype_ext(api_connection, asset_type_enum):
        """ Receives a list of assets with extended information

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={"asset_type_enum": str(asset_type_enum.value)}
        json_res = api_connection.exec_post_url('/api/assets/assetsbytype-ext/', payload)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df
