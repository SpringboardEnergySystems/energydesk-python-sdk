from energydeskapi.portfolios.portfoliotree_api import sample_portfolio_tree, sample_portfolio_tree_embedded
import json
import copy
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



def create_embedded_tree2(flat_tree):
    def lookup_node_by_id(id):
        for p in flat_tree:
            if p['portfolio_id']==id:
                return p
        return None # Not found

    def manage_node(node):
        children_as_json=[]
        for child in node['children']:
            child_node= lookup_node_by_id(child)
            cn=manage_node(child_node)
            children_as_json.append(cn)
        node['children']=children_as_json  # Replace list of INTs with list of json obj
        return copy.deepcopy(node)

    new_root=manage_node(flat_tree[0])
    result = json.dumps([new_root], indent=4)
    print(result)


def create_embedded_tree(flat_tree):
    root = 0
    for portf_tree in range(0, len(flat_tree)):
        portfolio_tree = flat_tree[portf_tree]
        if portfolio_tree['parent_id'] == 0:
            root += 1
        for child in range(0, len(portfolio_tree['children'])):
            child_portfolio = portfolio_tree['children'][child]
            portfolio_tree['children'][child] = flat_tree[child_portfolio - 1]
    for number_of_roots in range(0, len(flat_tree) - root):
        flat_tree.pop()
    result = json.dumps(flat_tree, indent=4)

    return result

def create_embedded_tree_for_dropdown(flat_tree):
    root = 0
    return []

if __name__ == '__main__':
    emb_tree = create_embedded_tree_for_dropdown(sample_portfolio_tree)
    print(emb_tree)

