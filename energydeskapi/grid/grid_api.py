import logging
from energydeskapi.assets.assets_api import AssetsApi
import pandas as pd
logger = logging.getLogger(__name__)


class GridMap:
    def __init__(self):
        self.pk = 0
        self.root_asset = None
        self.grid_map = None
    def get_dict(self, api_connection):
        dict = {}
        dict['pk'] = self.pk
        if self.root_asset is not None: dict['root_asset'] = AssetsApi.get_asset_url(api_connection, self.root_asset)
        if self.grid_map is not None: dict['grid_map'] = self.grid_map
        return dict
class GridApi:
    """ Class for assets

    """

    @staticmethod
    def get_grid_map_url(api_connection, gridmap_pk):
        """Fetches asset type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param grid_map_key: type of asset
        :type grid_map_key: int, required
        """

        return api_connection.get_base_url() + '/api/grid/gridmap/' + str(gridmap_pk) + "/"

    @staticmethod
    def get_gridmaps(api_connection, parameters={}):
        """Fetches asset type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """

        json_res = api_connection.exec_get_url('/api/grid/gridmap', parameters)
        return json_res
    @staticmethod
    def upsert_gridmap(api_connection, gridmap):
        """Registers/Updates asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset: asset object
        :type asset: str, required
        """
        logger.info("Upserting Gridmap")
        if gridmap.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/grid/gridmap/' + str(gridmap.pk) + "/", gridmap.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/grid/gridmap/', gridmap.get_dict(api_connection))
        return success, returned_data, status_code, error_msg
