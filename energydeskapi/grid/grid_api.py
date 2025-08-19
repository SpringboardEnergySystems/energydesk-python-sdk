import logging

from energydeskapi.sdk.api_connection import ApiConnection

from energydeskapi.assets.assets_api import AssetsApi
import pandas as pd
from energydeskapi.sdk.common_utils import key_from_url
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

class GridNode:
    def __init__(self):
        self.pk = 0
        self.asset = None
        self.sync_with_localmarket = False
        self.alternative_external_id=""
        self.alternative_external_name=""
        self.yearly_consumption=0
        self.customers_in_gridnode=0
        self.transformer1=0
        self.transformer2=0
        self.transformer3=0
        self.transformer4=0
        self.total_capacity=0
        self.n_minus_capacity=0
        self.peak_consumption=0

    def get_dict(self, api_connection):
        dict = {}
        dict['pk'] = self.pk
        if self.asset is not None: dict['asset'] = AssetsApi.get_asset_url(api_connection, self.asset)
        if self.sync_with_localmarket is not None: dict['sync_with_localmarket'] = self.sync_with_localmarket
        if self.alternative_external_id is not None: dict['alternative_external_id'] = self.alternative_external_id
        if self.alternative_external_name is not None: dict['alternative_external_name'] = self.alternative_external_name
        if self.yearly_consumption is not None: dict['yearly_consumption'] = self.yearly_consumption
        if self.customers_in_gridnode is not None: dict['customers_in_gridnode'] = self.customers_in_gridnode
        if self.transformer1 is not None: dict['transformer1'] = self.transformer1
        if self.transformer2 is not None: dict['transformer2'] = self.transformer2
        if self.transformer3 is not None: dict['transformer3'] = self.transformer3
        if self.transformer4 is not None: dict['transformer4'] = self.transformer4
        if self.total_capacity is not None: dict['total_capacity'] = self.total_capacity
        if self.n_minus_capacity is not None: dict['n_minus_capacity'] = self.n_minus_capacity
        if self.peak_consumption is not None: dict['peak_consumption'] = self.peak_consumption
        return dict


class GridNodeArming:
    def __init__(self):
        self.pk = 0
        self.grid_node = None
        self.period_from = None
        self.period_until=None


    def get_dict(self, api_connection):
        dict = {}
        dict['pk'] = self.pk
        if self.grid_node is not None: dict['grid_node'] = GridNode.get_grid_node_url(api_connection, self.grid_node)
        if self.period_from is not None: dict['period_from'] = self.period_from
        if self.period_until is not None: dict['period_until'] = self.period_until
        return dict

class GridApi:
    """ Class for assets

    """

    @staticmethod
    def get_grid_map_url(api_connection: ApiConnection, gridmap_pk):
        """Fetches asset type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param grid_map_key: type of asset
        :type grid_map_key: int, required
        """

        return api_connection.get_base_url() + '/api/grid/gridmap/' + str(gridmap_pk) + "/"

    @staticmethod
    def get_gridmaps(api_connection: ApiConnection, parameters={}):
        """Fetches asset type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """

        json_res = api_connection.exec_get_url('/api/grid/gridmap', parameters)
        return json_res
    @staticmethod
    def upsert_gridmap(api_connection: ApiConnection, gridmap):
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


    @staticmethod
    def get_capacity_coverage(api_connection: ApiConnection):
        """Registers/Updates asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset: asset object
        :type asset: str, required
        """
        logger.info("Retrieving coverage")
        json_res = api_connection.exec_get_url('/api/grid/gridcoverage/', {})
        return json_res

class GridNodeApi:
    """ Class for Grid Node assets
    """

    @staticmethod
    def get_grid_node_url(api_connection: ApiConnection, gridnode_pk):
        return api_connection.get_base_url() + '/api/grid/gridnodes/' + str(gridnode_pk) + "/"

    @staticmethod
    def register_grid_node(api_connection: ApiConnection, grid_node):
        asset_pk=AssetsApi.upsert_asset(api_connection, grid_node.asset)

        #return api_connection.get_base_url() + '/api/flexibility/gridnode/' + str(gridnode_pk) + "/"
    @staticmethod
    def upsert_grid_node(api_connection: ApiConnection, grid_node):

        logger.info("Upserting Gridnode")
        if grid_node.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/grid/gridnodes/' + str(grid_node.pk) + "/", grid_node.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/grid/gridnodes/', grid_node.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_grid_node_by_id(api_connection: ApiConnection, key):
        jdata = api_connection.exec_get_url(
                '/api/grid/gridnodes/' + str(key) + "/")
        gn=GridNode()
        gn.pk=jdata['pk']
        gn.asset = key_from_url(jdata['asset'])
        gn.sync_with_localmarket = jdata['sync_with_localmarket']
        gn.alternative_external_id = jdata['alternative_external_id']
        gn.alternative_external_name = jdata['alternative_external_name']
        gn.yearly_consumption = jdata['yearly_consumption']
        gn.customers_in_gridnode = jdata['customers_in_gridnode']
        gn.transformer1 = jdata['transformer1']
        gn.transformer2 = jdata['transformer2']
        gn.transformer3 = jdata['transformer3']
        gn.transformer4 = jdata['transformer4']
        gn.total_capacity = jdata['total_capacity']
        gn.n_minus_capacity = jdata['n_minus_capacity']
        gn.peak_consumption = jdata['peak_consumption']

        return gn

    @staticmethod
    def patch_grid_node(api_connection: ApiConnection, key, payload):
        success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/grid/gridnodes/' + str(key) + "/", payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_grid_nodes_arming(api_connection: ApiConnection, parameters={}):
        json_res = api_connection.exec_get_url('/api/grid/gridnodearming/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_grid_node_arming(api_connection: ApiConnection, grid_node_arming):

        logger.info("Upserting Gridnode arming")
        if grid_node_arming.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/grid/gridnodearming/' + str(grid_node_arming.pk) + "/", grid_node_arming.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/grid/gridnodearming/', grid_node_arming.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_grid_nodes_embedded(api_connection: ApiConnection, parameters={}):
        json_res = api_connection.exec_get_url('/api/grid/gridnodes/embedded/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_grid_nodes_with_embedded_tenders(api_connection: ApiConnection, parameters={}):
        json_res = api_connection.exec_get_url('/api/grid/gridnodes/tenders/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_grid_nodes(api_connection: ApiConnection, parameters={}):
        json_res = api_connection.exec_get_url('/api/grid/gridnodes/', parameters)
        if json_res is None:
            return None
        return json_res