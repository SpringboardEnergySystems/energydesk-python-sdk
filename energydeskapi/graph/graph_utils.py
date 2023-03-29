import networkx as nx
import pandas as pd

import logging
logger = logging.getLogger(__name__)

def get_all_paths(G):
    ownerperc = []
    individualperc = []
    leaves = list((v for v, d in G.out_degree() if d == 0))
    nodes = G.nodes()
    for leaf in leaves:
        for node in nodes:
            if nx.has_path(G, node, leaf) and node not in leaves:
                path_dict={"owner":node, "asset": leaf}
                path_list=[]
                #print("PATHS from", node, leaf)
                totp=0
                for path in nx.all_simple_paths(G, node, leaf):
                    path_sequence={"path_sequence":path}
                    path_elements = []
                    XP=1
                    for x in range(len(path)-1):
                        edge=G.get_edge_data(path[x], path[x+1])
                        #print("Simple path percentage; ", path[x], path[x+1], edge['percentage'])
                        path_elements.append({"from":path[x], "to":path[x+1], "percentage": edge['percentage']})
                        XP=XP*edge['percentage']
                    path_sequence['single_edge']=path_elements
                    path_sequence['calc_ownership'] = XP
                    #print("Full path percentage: ", path, XP)
                    path_list.append(path_sequence)
                    totp=totp+XP
                #print("Ownerrship from", node, leaf, totp)
                path_dict['paths']=path_list
                individualperc.append(path_dict)
                ownerperc.append({"company":node, "asset":leaf, "percentage":totp})
    #print(json.dumps(individualperc, indent=2))
    return ownerperc, individualperc

def calc_asset_ownerships(G):
    ownerperc, individualperc=get_all_paths(G)
    df = pd.DataFrame(data=ownerperc)
    return df


def calc_pivoted_asset_ownerships(G):
    df=calc_asset_ownerships(G)
    dfp = df.pivot(index='asset', columns='company', values='percentage')
    dfp=dfp.fillna(0)
    return dfp