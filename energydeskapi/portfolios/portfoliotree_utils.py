import json
import copy
from operator import itemgetter



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


def create_flat_tree2(embedded_tree):
    flat_list = []
    def manage_node(node):
        simple_children=[]
        for c in node['children']:
            manage_node(c)
            simple_children.append(c['portfolio_id'])
        node['children']=simple_children
        flat_list.append(copy.deepcopy(node))

    manage_node(embedded_tree[0])
    result = json.dumps(flat_list, indent=4)
    print(result)


from energydeskapi.sdk.common_utils import key_from_url
def create_embedded_tree_recursive(flat_tree):
    roots=[]
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
            "portfolio_id":node['pk'],
            "portfolio_name": node['description'],
            "percentage": 1,
            "portfolio_manager": node['manager']['name']
        }
        assets_as_json = []
        for a in node['assets']:
            assets_as_json.append({'asset_id': a['pk'],'asset_name': a['description'] })
        localnode['assets'] = assets_as_json

        tradingbooks_as_json = []
        for tb in node['trading_books']:
            tradingbooks_as_json.append({'tradingbook_id': tb['pk'],'tradingbook_name': tb['description'] })
        localnode['trading_books'] = tradingbooks_as_json
        children_as_json = []
        for child in node['sub_portfolios']:
            subkey=key_from_url(child)
            child_node= lookup_node_by_id(subkey)
            cn=manage_node(child_node)
            if cn is not None:
                children_as_json.append(cn)
        localnode['children']=children_as_json  # Replace list of INTs with list of json obj
        return localnode

    root=None
    for i in range(len(flat_tree)):
        if flat_tree[i]['parent_portfolio'] is None:
            new_root=manage_node(flat_tree[i])
            roots.append(new_root)

    return roots

def convert_nodes_from_jstree(portfolio_nodes):
    jstreelist = []
    ## TODO generate format for saving on API
    return jstreelist

def create_flat_tree_for_jstree(flat_tree):
    jstreelist=[]

    def create_node(node):
        percentage=1  # Defaul for now...
        parent="#" if node['parent_portfolio'] is None else key_from_url(node['parent_portfolio'])
        type_tag = "root" if node['parent_portfolio'] is None else "default"
        localnode = {
            "id": node['pk'],
            "text": node['description'] + "<span class=\'label label-default\'> " + str(percentage*100.0) + " %</span>",
            "type": type_tag,
            "parent": parent,
            "calculation": percentage,
            "state": {"opened": True},
            "portfolio_manager": node['manager']['name']
        }
        assets_as_json = []
        for a in node['assets']:
            assets_as_json.append({'asset_id': a['pk'],'asset_name': a['description'] })
        localnode['assets'] = assets_as_json

        tradingbooks_as_json = []
        for tb in node['trading_books']:
            tbnode={
                'id': tb['pk'],
                'text': tb['description'],
                "type":"trading_books",
                "data": [],
                "parent":node['pk']
            }
            tradingbooks_as_json.append(tbnode)
            #tradingbooks_as_json.append({'tradingbook_id': tb['pk'],'tradingbook_name': tb['description'] })
        localnode['trading_books'] = tradingbooks_as_json

        children_as_json = []
        for child in node['sub_portfolios']:
            subkey=key_from_url(child)
            children_as_json.append(subkey)
        localnode['children'] = children_as_json

        return localnode

    for i in range(len(flat_tree)):
        #if flat_tree[i]['parent_portfolio'] is None:
        dict_node=create_node(flat_tree[i])
        jstreelist.append(dict_node)

    return jstreelist


def create_embedded_tree_for_dropdown(flat_tree):
    roots=[]
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
            "portfolio_id":node['pk'],
            "title": node['description'],
            #"percentage": 1,
            #"portfolio_manager": node['manager']['name']
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
