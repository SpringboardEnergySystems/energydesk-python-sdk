import json
import copy
from energydeskapi.customers.customers_api import CustomersApi
#from energydeskapi.assets.assets_api import AssetsApi
#from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from operator import itemgetter
from energydeskapi.portfolios.portfolio_api import PortfolioNode
from energydeskapi.sdk.common_utils import remove_alpha_num
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
sample_portfolio_tree=[
  {
    "portfolio_id": 1,
    "name": "Trading Portfolios",
    "trading_books": [], # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [12,23],  # PKs of assets with FDM forecasts
    "parent_id": 0,
    "children": [2,5]
  },
  {
    "portfolio_id": 2,
    "name": "Trading Portfolios Nordic",
    "trading_books": [],  # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [12,23],  # PKs of assets with FDM forecasts
    "parent_id": 1,
    "children": [3,4]
  },
  {
    "portfolio_id": 3,
    "name": "Trading Book of Nick Leeson",
    "trading_books": [1], # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [],
    "parent_id": 2,
    "children": []
  },
  {
    "portfolio_id": 4,
    "name": "Trading Book of Warren Buffet",
    "trading_books": [2],  # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [],
    "parent_id": 2,
    "children": [6]
  },
  {
    "portfolio_id": 5,
    "name": "Trading Book German Power",
    "trading_books": [3,4],  # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [],
    "parent_id": 1,
    "children": []
  },
  {
    "portfolio_id": 6,
    "name": "Trading Book X",
    "trading_books": [3, 4],  # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [],
    "parent_id": 4,
    "children": [7]
  }
,
  {
    "portfolio_id": 7,
    "name": "Trading Book X",
    "trading_books": [3, 4],  # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [],
    "parent_id": 4,
    "children": [8]
  }
,
  {
    "portfolio_id": 8,
    "name": "Trading Book X",
    "trading_books": [3, 4],  # Different PKs than portfolios IDs.
    "percentage":1,
    "assets": [],
    "parent_id": 4,
    "children": []
  }
]


sample_portfolio_tree_embedded=[
  {
    "portfolio_id": 1,
    "name": "Trading Portfolios",
    "trading_books": [],  # Different PKs than portfolios IDs.
    "parent_id": 0,
    "children": [  {
                "portfolio_id": 2,
                "name": "Trading Portfolios Nordic",
                "trading_books": [],  # Different PKs than portfolios IDs.
                "percentage":1,
                "assets": [12,23],  # PKs of assets with FDM forecasts
                "parent_id": 1,
                "children": [
                  {
                    "portfolio_id": 3,
                    "name": "Trading Book of Nick Leeson",
                    "trading_books": [1],  # Different PKs than portfolios IDs.
                    "percentage":1,
                    "assets": [],
                    "parent_id": 2,
                    "children": []
                  },
                  {
                    "portfolio_id": 4,
                    "name": "Trading Book of Warren Buffet",
                    "trading_books": [2],  # Different PKs than portfolios IDs.
                    "percentage":1,
                    "assets": [],
                    "parent_id": 2,
                    "children": []
                  },
                ]
              },
              {
                "portfolio_id": 5,
                "name": "Trading Book German Power",
                "trading_books": [3, 4],  # Different PKs than portfolios IDs.
                "percentage":1,
                "assets": [],
                "parent_id": 1,
                "children": []
              }

    ]
  }
]

def create_flat_tree(embedded_tree):
    flat_list = []

    for embd_tree in range(0, len(embedded_tree)):
        embedded_tre = embedded_tree[embd_tree]
        print(embd_tree)
        for child in range(0, len(embedded_tre['children'])):
            portfolio_child = embedded_tre['children'][child]
            print(embedded_tre['children'][child])
            flat_list.append(embedded_tre['children'][child])
            embedded_tre['children'][child] = portfolio_child['portfolio_id']
    print(flat_list)

from energydeskapi.sdk.common_utils import key_from_url
def create_embedded_tree_recursive(flat_tree):
    roots=[]
    nodes_with_parents={}
    def lookup_node_by_id(id):
        for p in flat_tree:
            if p['pk']==id:
                #nd={"portfolio_id":p['pk'],"portfolio_name":p['description']}
                return p
        return None # Not found

    def manage_node(node):
        if node is None:
            return None

        localnode={
            "pk":node['pk'],
            "portfolio_name": node['description'],
            "percentage": 1,
            "portfolio_manager": node['manager']['name'],
            "portfolio_manager_id": node['manager']['pk']
        }
        assets_as_json = []
        for a in node['assets']:
            assets_as_json.append({'pk': a['pk'],'description': a['description'] })
        localnode['assets'] = assets_as_json

        tradingbooks_as_json = []
        for tb in node['trading_books']:
            tradingbooks_as_json.append({'pk': tb['pk'],'description': tb['description'] })
        localnode['trading_books'] = tradingbooks_as_json
        children_as_json = []
        for child in node['sub_portfolios']:
            print(child)
            subkey=key_from_url(child)
            if int(subkey) == node['pk']:
                continue
            #print("SUB", subkey)
            child_node= lookup_node_by_id(subkey)
            print("Child", child_node)
            cn=manage_node(child_node)
            cn['parent_id']=node['pk']
            nodes_with_parents[subkey]=subkey
            if cn is not None:
                children_as_json.append(cn)
        localnode['children']=children_as_json  # Replace list of INTs with list of json obj
        return localnode

    for i in range(len(flat_tree)):
        if flat_tree[i]['parent_portfolio'] is None:
            new_root=manage_node(flat_tree[i])
            roots.append(new_root)

    # CLEANUP
    new_roots=[]
    for r in roots:
        print(r)
        if r['pk'] in nodes_with_parents:
            continue
        new_roots.append(r)
    return new_roots


def convert_nodes_from_jstree(api_connection, portfolio_nodes):
    pmap={}
    portfolios=[]
    pmap_parents={}
    pnode= None
    for rec in portfolio_nodes:
        name=rec['data']['original_text'] if 'original_text' in rec['data'] else rec['text']
        if rec['type']=="default" or rec['type']=="root":
            node_id = int(rec['id'])
            pnode=PortfolioNode()
            pnode.description=name
            try:
                pnode.pk=0 if 'portfolio_id' not in rec['data'] else int(rec['data']['portfolio_id'])
            except:
                pnode.pk=0
            if "company" in rec['data'] and rec['data']['company'] is not None:
                pnode.manager=rec['data']['company']
            pmap[node_id]=pnode
        pid=0
        if rec['parent'] != "#":
            numpart = remove_alpha_num(rec['parent'])
            pid = int(numpart)
        if rec['type'] == "trading_books":
            for tbdata in rec['data']:
                tbid=0 if 'tradingbook_id' not in tbdata else int(tbdata['tradingbook_id'])
                if pnode is not None:
                    pnode.trading_books.append(tbid)
            continue
        if rec['type'] == "assets":
            for adata in rec['data']:
                print("Handling asset")
                asid=0 if 'asset_id' not in adata else int(adata['asset_id'])
                if pnode is not None:
                    pnode.assets.append(asid)
            continue
        if pid>0:
            if pid not in pmap_parents:
                pmap_parents[pid]=[]
            pmap_parents[pid].append(pnode)  # pnode added to parent pnode
        portfolios.append(pnode)

    for parkey in pmap_parents.keys():
        portnode = pmap[parkey]
        children=pmap_parents[parkey]
        for child in children:
            child.parent_id=portnode.pk
            child.parent_name = portnode.description
            portnode.sub_portfolios.append({'portfolio_id':child.pk,
                                         'portfolio_name':child.description})

    return portfolios


def create_flat_tree_for_jstree(flat_tree):
    jstreelist=[]

    def create_node(node):
        percentage=1  # Defaul for now...
        parent="#" if node['parent_portfolio'] is None else key_from_url(node['parent_portfolio'])
        type_tag = "root" if node['parent_portfolio'] is None else "default"
        localnode = {
            "id": node['pk'],
            "text": node['description'] + ' <span class=\'label label-default\'>' + str(percentage*100.0) + '%</span>',
            "type": type_tag,
            "data": {
                "original_text": node['description'],
                "calculation": str(percentage*100),
                "company": "4"
            },
            "parent": parent,
            "calculation": percentage,
            "state": {"opened": True}
        }
        assets_as_json = []
        for a in node['assets']:
            anode={
                "id": "pka"+str(a['pk']),
                "text": a['description'],
                "type": "assets",
                "data": [],
                "parent":node['pk']
            }
            jstreelist.append(anode)

        tradingbooks_as_json = []
        for tb in node['trading_books']:
            tbnode={
                "id": "pkt"+str(tb['pk']),
                "text": tb['description'],
                "type": "trading_books",
                "data": [],
                "parent":node['pk']
            }
            jstreelist.append(tbnode)


        return localnode

    for i in range(len(flat_tree)):
        #if flat_tree[i]['parent_portfolio'] is None:
        dict_node=create_node(flat_tree[i])
        jstreelist.append(dict_node)

    return jstreelist


def convert_embedded_tree_to_jstree(embedded_tree):
    jstreelist=[]
    node_ids={"portfolio_node_id":1, "tradingook_node_id":1, "asset_node_id":1}
    portfolio_node_map={}
    def create_node(node, parent, node_ids, portfolio_node_map):
        percentage=1  # Defaul for now...
        portfolio_node_map[node_ids['portfolio_node_id']]=node['pk']
        type_tag = "root" if "parent_id" not in node or node['parent_id'] is None else "default"
        localnode = {
            "id": node_ids['portfolio_node_id'],
            "text": node['portfolio_name'] + " (" + str(node['pk'])  + ") "+ ' <span class=\'label label-default\'>' + str(percentage*100.0) + '%</span>',
            "type": type_tag,
            "data": {
                "original_text": node['portfolio_name'],
                "calculation": str(percentage*100),
                "company": node['portfolio_manager_id'],
                "portfolio_id": node['pk']  #This may be duplicated in the tree if added several places
            },
            "parent": parent,
            "calculation": percentage,
            "state": {"opened": True}
        }
        current_portfolio_parent=node_ids['portfolio_node_id']
        node_ids['portfolio_node_id']+=1

        for a in node['assets']:
            anode={
                "id": "pka" + str(node_ids['asset_node_id']),#"pka"+str(a['pk']),
                "text": a['description'],
                "type": "assets",
                "data": [{'asset_id': a['pk']}],
                "parent":current_portfolio_parent
            }
            jstreelist.append(anode)
            node_ids['asset_node_id'] += 1

        for tb in node['trading_books']:
            tbnode={
                "id": "pkt"+str(node_ids['tradingook_node_id']),
                "text": tb['description'],
                "type": "trading_books",
                "data": [{'tradingbook_id': tb['pk']}],
                "parent":current_portfolio_parent
            }
            node_ids['tradingook_node_id']+=1
            jstreelist.append(tbnode)
        return localnode

    def parse_embedded_node(emb_node,parent, node_ids, portfolio_node_map):
        dict_node=create_node(emb_node, parent, node_ids, portfolio_node_map)
        jstreelist.append(dict_node)
        for ch in emb_node['children']:
            parse_embedded_node(ch, dict_node['id'], node_ids, portfolio_node_map)
        return node_ids

    for i in range(len(embedded_tree)):
        node_ids=parse_embedded_node(embedded_tree[i],"#", node_ids, portfolio_node_map)
    return jstreelist


def create_embedded_tree_for_dropdown(flat_tree):
    roots=[]
    def lookup_node_by_id(id):
        for p in flat_tree:
            if p['pk']==id:
                return p
        return None # Not found

    def manage_node(node):
        if node is None:
            return None

        localnode={
            "portfolio_id":node['pk'],
            "title": str(node['pk']) + " " + node['description'],
        }
        children_as_json = []
        for child in node['sub_portfolios']:
            subkey=key_from_url(child)
            child_node= lookup_node_by_id(subkey)
            cn=manage_node(child_node)
            if cn is not None:
                children_as_json.append(cn)
        localnode['data']=children_as_json  # Replace list of INTs with list of json obj
        return localnode

    root=None
    for i in range(len(flat_tree)):
        if flat_tree[i]['parent_portfolio'] is None:
            new_root=manage_node(flat_tree[i])
            roots.append(new_root)
    return roots



def create_embedded_tree(flat_tree):
    root = 0
    for portf_tree in range(0, len(flat_tree)):
        portfolio_tree = flat_tree[portf_tree]
        if portfolio_tree['parent_id'] == 0:
            root += 1
        for child in range(0, len(portfolio_tree['children'])):
            child_portfolio = portfolio_tree['children'][child]
            portfolio_tree['children'][child] = flat_tree[child_portfolio - 1]
    sorted_tree = sorted(flat_tree, key=itemgetter('parent_id'))
    for number_of_roots in range(0, len(sorted_tree) - root):
        sorted_tree.pop()
    result = json.dumps(sorted_tree, indent=4)

    return result


def create_embedded_dropdown2(flat_tree):
    def lookup_node_by_id(id):
        for p in flat_tree:
            if p['portfolio_id']==id:
                return p
        return None # Not found

    def manage_node(node):
        localnode={}
        localnode['title']=node['name']
        localnode['portfolio_id'] = node['portfolio_id']
        localnode['data']=[]

        children_as_json=[]
        for child in node['children']:
            child_node= lookup_node_by_id(child)
            cn=manage_node(child_node)
            children_as_json.append(cn)
        localnode['data']=children_as_json  # Replace list of INTs with list of json obj
        return copy.deepcopy(localnode)

    new_root=manage_node(flat_tree[0])
    result = json.dumps([new_root], indent=4)
    print(result)
    return result

def create_embedded_tree_for_dropdown2(flat_tree):
    root = 0
    resultlist=[]
    for portf_tree in range(0, len(flat_tree)):
        portfolio_tree = flat_tree[portf_tree]
        if portfolio_tree['parent_id'] == 0:
            root += 1
        localnode={}
        localnode['title']=flat_tree[portf_tree]['name']
        localnode['dataAttrs']=[]
        for child in range(0, len(portfolio_tree['children'])):
            child_portfolio = portfolio_tree['children'][child]
            portfolio_tree['children'][child] = flat_tree[child_portfolio - 1]
            child={}
            child['name']=flat_tree[child_portfolio - 1]['name']
            child['dataAttrs']=[]
            localnode['dataAttrs'].append(child)
        resultlist.append(localnode)
    for number_of_roots in range(0, len(flat_tree) - root):
        flat_tree.pop()
    result = json.dumps(resultlist, indent=4)
    #print(json.dumps(resultlist, indent=4))
    return result

if __name__ == '__main__':
    emb_tree = create_embedded_dropdown2(sample_portfolio_tree)
    print(emb_tree)
