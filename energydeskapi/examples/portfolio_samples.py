
import logging
import json
from energydeskapi.portfolios.portfolio_api import PortfoliosApi
from energydeskapi.portfolios.portfolio_api import PortfolioNode
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
        #print("PPORT", p, p.trading_books)
        print(json.dumps(p.get_dict(api_conn), indent=4))
        PortfoliosApi.upsert_portfolio(api_conn, p)

    #print(result_json)
    #print(json.dumps(result_json, indent=4))

def load_portfolio(api_conn):
    ut=PortfoliosApi.get_portfolios_embedded(api_conn)
    print(ut)

def query_portfolios(api_conn):
    x=PortfolioTreeApi.get_portfolio_tree(api_conn)
    #print(json.dumps(x, indent=4))

    x2=convert_embedded_tree_to_jstree(x)
    print("Ready")
    #print(json.dumps(x2, indent=4))
    print("DONE")
    #save_conversion(api_conn, x2)
    #js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    #print(json.dumps(js, indent=4))
    #x=create_flat_tree_for_jstree(js)
    res=PortfolioTreeApi.get_portfolio_tree_for_dropdown(api_conn)
    print(json.dumps(res, indent=4))

    return
    js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    print(json.dumps(js, indent=4))
    query_portfolios(api_conn, js)

def create_portfolio(api_conn):
    d={'pk': 0, 'description': 'Fuels', 'portfolio_name': 'Fuels', 'trading_books': [], 'manager': None, 'assets': [], 'sub_portfolios': [], 'stakeholders': [], 'parent_portfolio': 'http://127.0.0.1:8001/api/portfoliomanager/portfolios/2/'}
    pnode=PortfolioNode()
    pnode.description="Fuel"
    pnode.parent_id=2
    #print(pnode.get_dict(api_conn))
    print(json.dumps(pnode.get_dict(api_conn), indent=4))
    PortfoliosApi.upsert_portfolio(api_conn, pnode)

def create_empty(api_conn):
    pnode = PortfolioNode()
    pnode.description = "Root"
    pnode.pk = 0
    pnode.manager = 197
    tree = [pnode]
    success = PortfolioTreeApi.upsert_portfolio_tree(api_conn, tree)


def load_tree(api_conn):

    js=open("./ptree.json","r").read()
    jss=json.loads(js)
    #print(json.dumps(jss, indent=4))
    save_conversion(api_conn,jss)

if __name__ == '__main__':
    api_conn=init_api()
    #load_tree(api_conn)
    #create_empty(api_conn)
    query_portfolios(api_conn)
