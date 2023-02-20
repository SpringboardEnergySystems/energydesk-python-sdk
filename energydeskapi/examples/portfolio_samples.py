
import logging
import json
from energydeskapi.portfolios.portfolio_api import PortfoliosApi
from energydeskapi.portfolios.portfoliotree_api import PortfolioTreeApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.portfolios.portfoliotree_utils import convert_nodes_from_jstree,convert_embedded_tree_to_jstree, create_flat_tree_for_jstree,create_embedded_tree_recursive, create_embedded_tree_for_dropdown
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def save_conversion(api_conn, portfolio_nodes):
    pnodes = convert_nodes_from_jstree(api_conn, portfolio_nodes)
    for p in pnodes:

        print(json.dumps(p.get_dict(api_conn), indent=4))
        PortfoliosApi.upsert_portfolio(api_conn, p)
        return
    #print(result_json)
    #print(json.dumps(result_json, indent=4))


def query_portfolios(api_conn):
    x=PortfolioTreeApi.get_portfolio_tree(api_conn)
    print(json.dumps(x, indent=4))
    x2=convert_embedded_tree_to_jstree(x)
    print(json.dumps(x2, indent=4))
    #save_conversion(api_conn, x2)
    #js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    #print(json.dumps(js, indent=4))
    #x=create_flat_tree_for_jstree(js)


    return
    js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    print(json.dumps(js, indent=4))
    query_portfolios(api_conn, js)


def load_tree(api_conn):

    js=open("./ptree.json","r").read()
    jss=json.loads(js)
    print(json.dumps(jss, indent=4))
    save_conversion(api_conn,jss)

if __name__ == '__main__':
    api_conn=init_api()
    load_tree(api_conn)
