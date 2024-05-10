import pandas as pd
import logging
from django.conf import settings
from energydeskapi.types.company_enum_types import UserRoleEnum
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.customers.users_api import UsersApi, User, UserGroup
from energydeskapi.customers.customers_api import CustomersApi

import logging
import json

import pandas as pd

from energydeskapi.portfolios.portfolio_api import PortfoliosApi
from energydeskapi.portfolios.portfolio_api import PortfolioNode
from energydeskapi.portfolios.portfoliotree_api import PortfolioTreeApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.portfolios.portfoliotree_utils import convert_nodes_from_jstree,convert_embedded_tree_to_jstree, create_flat_tree_for_jstree,create_embedded_tree_recursive, create_embedded_tree_for_dropdown
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded
from energydeskapi.assets.assets_api import AssetsApi
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
import sys

def load_flat_tree(api_conn):

    #print(json.dumps(output, indent=4))
    output=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    backagain=convert_nodes_from_jstree(api_conn, output)
    for node in backagain:
        print( node.pk, "(", node.description,")", node.sub_portfolios)

    return backagain

from copy import copy, deepcopy

def update_flat_tree(api_conn, nodes):
    comps = CustomersApi.get_companies_compact(api_conn,
                                       {'registry_number': '977296919'})
    if comps is None or len(comps['results']) == 0:
        return None
    comp_pk = comps['results'][0]['pk']
    print("Assigning company key", comp_pk)

    for node in nodes:
        if node.description=="HEV Hedging Exchange":
            print("So far")
            n1 = deepcopy(node)
            n1.pk=0
            n1.portfolio_id = None
            n1.description="E-CO Vannkraft_Hedging"
            n1.trading_books=[node.trading_books[0]]
            n2 = deepcopy(node)
            n2.pk=0
            n2.portfolio_id = None
            n2.description = "E-CO Vannkraft_Hedging 2"
            n2.trading_books = [node.trading_books[1]]
            nodes.append(n1)
            nodes.append(n2)
            node.sub_portfolios.append({'portfolio_id':0, 'portfolio_name':n1.description})
            node.sub_portfolios.append({'portfolio_id':0, 'portfolio_name':n2.description})
            node.trading_books=[]
            #print(json.dumps(node.get_dict(api_conn), indent=4))
    found={}
    dictlist = []
    for p in nodes:
        if p.manager is None or p.manager == 0:
            p.manager = comp_pk

        if p.pk==0 or p.pk not in found:
            found[p.pk]=p.pk
            dictlist.append(p.get_dict(api_conn))
            print(json.dumps(p.get_dict(api_conn), indent=4))
    PortfolioTreeApi.upsert_portfolio_tree_from_flat_dict(api_conn, dictlist)




def query_portfolios(api_conn):
    #x=PortfolioTreeApi.get_portfolio_tree(api_conn)
    #x2=convert_embedded_tree_to_jstree(x)
    ps=PortfoliosApi.get_portfolios(api_conn)
    print(ps)
    df=pd.DataFrame(data=ps)
    print(df)

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
    tree=load_flat_tree(api_conn)
    update_flat_tree(api_conn, tree)
