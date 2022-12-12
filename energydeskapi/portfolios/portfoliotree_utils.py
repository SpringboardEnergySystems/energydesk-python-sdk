from energydeskapi.portfolios.portfoliotree_api import sample_portfolio_tree


def create_embedded_tree(flat_tree):
    print(flat_tree)



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
    create_embedded_tree(sample_portfolio_tree)