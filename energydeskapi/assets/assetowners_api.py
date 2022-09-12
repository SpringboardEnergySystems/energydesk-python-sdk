import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class AssetOwnersApi:
    """ Class for asset owners

    """

    # Create a json file from NetworkX DiGraph defining ownerships
    @staticmethod
    def save_ownerships(api_connection, ownership_graph_json):
        """Saves ownership of asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param ownership_graph_json: description...
        :type ownership_graph_json: str, required
        """
        json_res=api_connection.exec_post_url('/api/asset-ownership/save-ownership-graph/', ownership_graph_json)

    @staticmethod
    def load_ownerships(api_connection):
        """Loads ownership of asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/asset-ownership/load-ownership-graph/')
        return json_res

    @staticmethod
    def get_asset_ownerships(api_connection):
        """Receives ownership of assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/asset-ownership/get-asset-ownerships/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=eval(json_res))
        return df

    @staticmethod
    def get_asset_ownerships_pivoted(api_connection):
        """Description...

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/asset-ownership/get-asset-ownerships-pivoted/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=eval(json_res))
        return df

    @staticmethod
    def all_asset_ownership_paths(api_connection):
        """Receives the path of every asset ownerships

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/asset-ownership/all-ownership-paths/')
        return json_res
