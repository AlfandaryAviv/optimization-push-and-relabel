import pickle
import os
import networkx as nx
import math
import csv
# import operator
# import random
# import numpy as np

def push_and_relabel():
    # file_path = "./data/road-euroroad_with_weight_2_py.csv"
    file_path = "./data/road-euroroad_with_weight_updated_edges.csv"
    # file_path = "./data/road-euroroad_with_weight_original.csv"

    datalines = open(file_path, 'r').readlines()
    datalines = [row.replace('\n', '').split(',') for row in datalines]

    src, dst, weight = zip(*datalines)

    int_src = list(map(int, src))
    int_dst = list(map(int, dst))
    int_weight = list(map(int, weight))

    g = nx.DiGraph()
    for n1, n2, w in zip(int_src, int_dst, int_weight):

        # Initialize height and excess flow of every vertex as 0.
        g.add_node(n1, excess=0, height=0)
        g.add_node(n2, excess=0, height=0)

        # Initialize flow of every edge as 0 and capacity to w.
        g.add_edge(n1, n2, capacity=w, flow=0)

    # remove vertices which are not accessible from vertex 100
    length = dict(nx.all_pairs_shortest_path_length(g))
    new_nodes = set(k for k in length[100])

    for n in list(g.nodes()):
        if n not in new_nodes:
            g.remove_node(n)

    print(f"num nodes: {g.number_of_nodes()}, num edges: {g.number_of_edges()}")

    # create new indexes for the nodes (setting our original source(100) to be idx 1)
    mapping = {n: i + 1 for i, n in enumerate(g.nodes())}
    mapping[100], mapping[1] = mapping[1], mapping[100]
    g = nx.relabel_nodes(g, mapping)

    writer = csv.writer
    out_file = open(f"./data/for_gephi_small_{g.number_of_nodes()}_nodes_{g.number_of_edges()}_edges.csv", 'w')
    for e in g.edges():
        new_row = [str(e[0]), str(e[1])]
        r = ','.join(new_row)
        out_file.write(r + '\n')
    out_file.close()


    #####################################################
    ## if we want to use 499 as target with 504 index
    # inverse_mapping = {v: k for k,v in mapping.items()}
    # mapping[499], mapping[inverse_mapping[504]] = mapping[inverse_mapping[504]], mapping[499]
    # g = nx.relabel_nodes(g, mapping)
    ####################################################

    source, target = 1, 100
    print(f"starting push and relabel max flow with source: {source}, target: {target}")
    solve_push_and_relabel(g, source, target)

    '''
    # p = nx.shortest_path(g)
    # length = dict(nx.all_pairs_shortest_path_length(g))

    # ######## find network with a size > 500
    # maxi=0
    # for i in range(1,len(length)+1):
    #     try:
    #         max_value = len(length[i])
    #         # if max_value > maxi:
    #         if max_value > 500:
    #             maxi = max_value
    #             print(maxi, i)
    #     except:
    #         e=0

    # ### finds longest path from each node
    # maxi = 0
    # for i in length:
    #     max_value = max(length[i].values())  # maximum value
    #     if max_value > maxi:
    #         maxi = max_value
    #         max_keys = [k for k, v in length[i].items() if v == max_value]
    #         print(maxi, i, max_keys)

    ### find nodes with in deg higher than 3
    # for node in g.nodes():
    #     if g.in_degree(node)>3:
    #         print(f"node: {node}, in_degree:{g.in_degree(node)}, out_dergree: {g.out_degree(node)}")
    '''




    ''' 
    # find the longest path and the edges (path: 67, src:634, dst: 828)
    length = dict(nx.all_pairs_shortest_path_length(g))
    maxi = 0
    for i in length:
        max_value = max(length[i].values()) # maximum value
        if max_value > maxi:
            maxi = max_value
            max_keys = [k for k, v in length[i].items() if v == max_value]
            print(maxi, i, max_keys)
    '''

    ''' 
    # create new edges file 
    sampled_indices = random.sample([i for i in range(g.number_of_nodes())], 2)
    nodes = list(g.nodes())
    
    nodes_to_connect = set()
    for n in g.nodes():
        if g.degree[n]<2:
            nodes_to_connect.add(n)
    
    e=0
    pair = list()
    for n in nodes_to_connect:
        new_connect = list(i for i in nodes_to_connect if i != n)
        new_edge = random.sample(new_connect, 1)
        g.add_edge(n,new_edge[0])
        pair.append((n,new_edge[0]))
    
    
    ed_file = open("./data/road-euroroad_with_weight_2_py.csv", 'r')
    out_file = open("./data/road-euroroad_with_weight_updated_edges.csv", 'w')
    
    writer = csv.writer
    lines = ed_file.readlines()
    for row in lines:
        out_file.write(row)
    
    for p in pair:
        new_row = [str(p[0]),str(p[1])]
        cur_random = random.randint(50, 300)
        new_row.extend([str(cur_random)])
        row_with_weight = ','.join(new_row)
        out_file.write(row_with_weight+'\n')
    '''


def push(graph, node):
    """
    flow from a node which has excess flow. If a node has excess flow and there is an adjacent with smaller height in
    the residual graph, push the flow from the node to the adjacent with lower height.
    """
    push_accomplished = False
    for edge in graph.out_edges(node):
        adjacent = edge[1]
        if graph.edges()[edge]["capacity"] - graph.edges()[edge]["flow"] > 0 and \
                graph.nodes()[node]["height"] > graph.nodes()[adjacent]["height"]:

            push_accomplished = True
            reverse_edge = (edge[1], edge[0])

            push_flow = min(graph.nodes()[node]["excess"],
                            graph.edges()[edge]["capacity"] - graph.edges()[edge]["flow"])
            graph.edges()[edge]["flow"] += push_flow
            graph.edges()[reverse_edge]["flow"] -= push_flow
            graph.nodes()[adjacent]["excess"] += push_flow
            graph.nodes()[node]["excess"] -= push_flow

            print(f"push {push_flow} from {node} to {adjacent}")
            if graph.nodes()[node]["excess"] == 0:
                break
    return push_accomplished


def relabel(graph, node):
    """
    Used to make a push() possible.
    Increases the height of the node with excess flow that none of its adjacent has lower height.
    To increase height, we pick the minimum height adjacent and add +1 to it.
    """
    min_height = math.inf

    for edge in graph.out_edges(node):
        if graph.edges()[edge]["flow"] - graph.edges()[edge]["capacity"] == 0:
            continue
        if graph.nodes()[edge[1]]["height"] < min_height:
            min_height = graph.nodes()[edge[1]]["height"]
        graph.nodes()[node]["height"] = min_height + 1

    print(f">> Relabel {node} to height {graph.nodes()[node]['height']}")


def solve_push_and_relabel(graph, source_node, target_node):
    """
    Run push-relabel max flow algorithm for the given graph with source and target node.
    :param graph: Networkx undirected graph (Digraph)
    :param source_node: Source node (int)
    :param target_node: Target node (int)
    """

    # Initialize height of source vertex equal to total number of vertices in graph.
    s = graph.nodes()[source_node]
    s["height"] = len(graph.nodes())

    # Create temp edges
    for e in graph.edges():
        if not graph.has_edge(e[1], e[0]):
            graph.add_edge(e[1], e[0], capacity=0, flow=0, tmp=True)

    # Initialize edges from source node
    for e in graph.out_edges(source_node):
        graph.edges()[e]["flow"] = graph.edges()[e]["capacity"]
        graph.nodes()[e[1]]["excess"] = graph.edges()[e]["flow"]
        graph.edges()[(e[1], e[0])]["flow"] = -graph.edges()[e]["capacity"]

    # run push and relabel
    while True:
        node = None
        for n in graph.nodes():
            if n != target_node and n != source_node and graph.nodes()[n]["excess"] > 0:
                node = n
                break
        if node is None:
            break
        succeed_push = push(graph, node)
        if not succeed_push:
            relabel(graph, node)

    path = "./pkl"
    if not os.path.exists(path):
        os.makedirs(path)

    # Save graph
    pickle.dump(graph, open(f"{path}/graph_{str(source_node)}_{str(target_node)}_{str(graph.number_of_nodes())}_"
                            f"{str(graph.number_of_edges())}.pkl", "wb"))

    # Remove temp edges
    for edge in graph.edges():
        if hasattr(edge, "tmp"):
            graph.remove_edge(edge)

    # Save graph after removing tmp edges
    pickle.dump(graph, open(f"{path}/graph_{str(source_node)}_{str(target_node)}_{str(graph.number_of_nodes())}_"
                            f"{str(graph.number_of_edges())}.pkl", "wb"))

    # Total flow from source
    print(f"total flow from source: {graph.nodes()[source_node]}")

    # Total flow to target
    print(f"total flow to target: {graph.nodes()[target_node]}")


if __name__ == '__main__':
    push_and_relabel()
