import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.assetowners_api import AssetOwnersApi
from networkx.readwrite import json_graph
import json
from energydeskapi.graph.graph_utils import get_all_paths, calc_asset_ownerships
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def load_digraph_of_ownerships(api_conn):

    digraph=AssetOwnersApi.load_ownerships(api_conn)
    G = json_graph.node_link_graph(json.loads(digraph['ownership_graph']))

    #print({node: list(G[node]) for node in G})
    a,b=get_all_paths(G)
    print(a)
    df=calc_asset_ownerships(G)
    print(df)

def get_asset_owners_info(api_conn):
    df=AssetOwnersApi.get_asset_ownerships(api_conn)
    print("Asset ownerships", df)



if __name__ == '__main__':

    api_conn=init_api()
    load_digraph_of_ownerships(api_conn)
    #get_asset_owners_info(api_conn)
