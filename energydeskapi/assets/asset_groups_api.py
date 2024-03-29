import logging
import pandas as pd
logger = logging.getLogger(__name__)
from energydeskapi.assets.assets_api import AssetsApi
#fields = ['pk', 'asset_id', 'extern_asset_id', 'description', 'asset_type', 'grid_connection', 'power_supplier',
 #         'asset_owner', 'asset_manager', 'meter_id', 'sub_meter_id', 'vendor', 'is_active']

class AssetGroup:
    def __init__(self):
        self.pk=0
        self.description=None
        self.main_asset=None
        self.sub_assets=[]
        self.valid_from=None
        self.valid_until=None

    def get_dict(self, api_connection):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.main_asset is not None: dict['main_asset'] = AssetsApi.get_asset_url(api_connection,self.main_asset)
        subs=[]
        for sub in self.sub_assets:
            subs.append(AssetsApi.get_asset_url(api_connection, sub))
        dict['sub_assets'] = subs
        if self.valid_from is not None: dict['valid_from'] = self.valid_from
        if self.valid_until is not None: dict['valid_until'] = self.valid_until
        return dict

class AssetGroupApi:
    """ Class for asset groups
    """

    @staticmethod
    def upsert_asset_group(api_connection, asset_group):
        """Registers/Updates asset_group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset: asset object
        :type asset: str, required
        """
        logger.info("Upserting assetgroups")
        if asset_group.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/assets/assetgroups/' + str(asset_group.pk) + "/", asset_group.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/assets/assetgroups/', asset_group.get_dict(api_connection))
        return success, returned_data, status_code, error_msg


    @staticmethod
    def get_asset_groups(api_connection, parameters={}):
        """Fetches all assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assetgroups/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def delete_asset_group(api_connection, pk):
        """Deletes an assset group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        success, returned_data, status_code, error_msg = api_connection.exec_delete_url('/api/assets/assetgroups/' + str(pk) + "/")
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_asset_groups_embedded(api_connection, parameters={}):
        """Fetches all assets with extended information

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assetgroups/embedded', parameters)
        return json_res
