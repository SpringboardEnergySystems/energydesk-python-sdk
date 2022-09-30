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
    def save_ownerships(api_connection, asset_manager_pk, ownership_graph_jsonstr):
        """Saves ownership of asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param ownership_graph_json: description...
        :type ownership_graph_json: str, required
        """
        payload={
            "ownership_graph": ownership_graph_jsonstr,
            "asset_manager_pk": asset_manager_pk
        }
        json_res=api_connection.exec_post_url('/api/asset-ownership/save-ownership-graph/', payload)
        logger.info(str(json_res))


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
        """Fetches ownership of all assets

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
        """Fetches pivoted ownerships of all assets

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
        """Fetches the path all asset ownerships

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/asset-ownership/all-ownership-paths/')
        return json_res
