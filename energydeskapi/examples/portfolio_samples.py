
import logging
import json
from energydeskapi.portfolios.portfoliotree_api import PortfolioTreeApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.portfolios.portfoliotree_utils import convert_nodes_from_jstree,convert_embedded_tree_to_jstree, create_flat_tree_for_jstree,create_embedded_tree_recursive, create_embedded_tree_for_dropdown
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def save_conversion(api_conn, portfolio_nodes):
    result_json = convert_nodes_from_jstree(portfolio_nodes)
    print(result_json)

def query_portfolios(api_conn):
    x=PortfolioTreeApi.get_portfolio_tree(api_conn)
    print(json.dumps(x, indent=4))
    x2=convert_embedded_tree_to_jstree(x)
    print(json.dumps(x2, indent=4))
    #js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    #print(json.dumps(js, indent=4))
    #x=create_flat_tree_for_jstree(js)


    return
    js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    print(json.dumps(js, indent=4))
    save_conversion(api_conn, js)




if __name__ == '__main__':
    api_conn=init_api()
    query_portfolios(api_conn)
