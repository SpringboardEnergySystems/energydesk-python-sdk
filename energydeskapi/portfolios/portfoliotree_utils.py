from energydeskapi.portfolios.portfoliotree_api import sample_portfolio_tree, sample_portfolio_tree_embedded
import json

def create_flat_tree(embedded_tree):
    flat_list = []


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
    result = json.dumps(flat_tree, indent=2)

    return result
    tree=[]

    root=None
    #Find parent
    for n in flat_tree:
        if n.parent_id==0:
            root=n
            break

    def embedd_node(node):
        newnode=node.copy(deepcopy=True)
        newnode.children=[]  # In this new copy we will not store INTs but embedded json
        for c in node.children:
            print(c.name)
            newnode.children.append(c)

            embedd_node(c)  #Looks funny, but now we manage the sub node before we have finished the current one
        tree.append(node)  # Adds the new copy to the new list after we have completed this node and its children

    embedd_node(root)



if __name__ == '__main__':
    emb_tree = create_embedded_tree(sample_portfolio_tree)
    print(emb_tree)
    # create_flat_tree(sample_portfolio_tree_embedded)
    # print(flt_tree)
