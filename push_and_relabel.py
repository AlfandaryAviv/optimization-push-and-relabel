import pickle
import os
import networkx as nx
from networkx.algorithms.flow import preflow_push, edmonds_karp, shortest_augmenting_path
# import csv
# import operator
# import random
# import numpy as np

def push_and_relabel():

    # file_path = "./data/road-euroroad_with_weight_2_py.csv"
    file_path = "./data/road-euroroad_with_weight_updated_edges.csv"

    datalines = open(file_path, 'r').readlines() #[2:]
    datalines = [row.replace('\n', '').split(',') for row in datalines]

    src, dst, weight = zip(*datalines)

    int_src = list(map(int, src))
    int_dst = list(map(int, dst))
    int_weight = list(map(int, weight))

    # nodes = set(list(src) + list(dst))
    # nodes = sorted(list(nodes))

    g = nx.DiGraph()
    for n1, n2, w in zip(int_src, int_dst, int_weight):
        g.add_node(n1, overrun=0, dist=0)
        g.add_node(n2, overrun=0, dist=0)
        g.add_edge(n1, n2, capacity=w, load=0)

    solve_max_flow(g, 7, 10)

    ################################################################################
    # ########### ***********comapare algorithm results to others:******************
    #
    # # comapre to nx Preflow-Push  #todo: check if its the same as push and relabel
    # R = preflow_push(g, 7, 10)
    # flow_value = nx.maximum_flow_value(g, 7, 10)
    # print("flow from nx maxflow algo: ",flow_value)
    #
    # # admonds_karp
    # R_admonds_karp = edmonds_karp(g, 7, 10)
    # flow_value_admonds_karp = nx.maximum_flow_value(g, 7, 10)
    # print("flow from nx algo: ",flow_value_admonds_karp)
    #
    # # shortest_augmenting_path
    # R_shortest_augmenting_path = shortest_augmenting_path(g, 7, 10)
    # flow_value_shortest_augmenting_path = nx.maximum_flow_value(g, 7, 10)
    # print("flow from nx algo: ",flow_value_shortest_augmenting_path)
    #
    # ##### more nx implementation are here: https://networkx.org/documentation/stable//reference/algorithms/flow.html?highlight=flow#module-networkx.algorithms.flow
    #################################################################################

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

    # solve_max_flow(g,634,828)

    # random.seed(0)
    # sampled_indices = random.sample([i for i in range(g.number_of_nodes())], 2)
    # print(sampled_indices)
    # solve_max_flow(g,sampled_indices[0],sampled_indices[1])

def get_active_node(graph, source_node, target_node):
    for node in graph.nodes():
        if not node is target_node and not node is source_node and graph.nodes()[node]["overrun"] > 0:
            return node
    return None

def has_active_node(graph, s, t):
    return True if not get_active_node(graph, s, t) is None else False

def push(graph, node):
    '''
    Push a load from the given node if possible.
    If a neighbor node which is closer the target node can accept more load - push.
    Else, if no such node is found push fails therefore a relabel is executed.
    '''
    success = False
    for edge in graph.out_edges(node):
        neighbor = edge[1]
        if not graph.nodes()[node]["dist"] == graph.nodes()[neighbor]["dist"] + 1 or graph.edges()[edge]["load"] == graph.edges()[edge]["capacity"]:
            continue
        success = True
        reverse_edge = (edge[1], edge[0])

        push = min(graph.edges()[edge]["capacity"] - graph.edges()[edge]["load"], graph.nodes()[node]["overrun"])
        graph.edges()[edge]["load"] += push
        graph.edges()[reverse_edge]["load"] -= push
        graph.nodes()[neighbor]["overrun"] += push
        graph.nodes()[node]["overrun"] -= push

        print(f"pushing {push} from {node} to {neighbor}")
        if graph.nodes()[node]["overrun"] == 0:
            break

    return success

def relabel(graph, node):
    """
    Relabel a node.
    Finds smallest dist in order to make a push possible.
    Adjusts the dist value of the current node to the minimun dist value of its neighbors plus one.
    """
    min_dist = None

    for edge in graph.out_edges(node):
        if graph.edges()[edge]["load"] == graph.edges()[edge]["capacity"]:
            continue
        if min_dist is None or graph.nodes()[edge[1]]["dist"] < min_dist:
            min_dist = graph.nodes()[edge[1]]["dist"]

        graph.nodes()[node]["dist"] = min_dist + 1

def solve_max_flow(graph, source_node, target_node):
    '''
    Solves the max flow prolem using the push-relabel algorithm for the given
    graph and source/target node.
    :param graph: a networkx undirected graph
    :param source_node: int, the source node
    :param target_node: int, the target node
    '''
    s = graph.nodes()[source_node]

    for n in graph.nodes():
        graph.nodes()[n]["dist"] = 0
        graph.nodes()[n]["overrun"] = 0

    for e in graph.edges():
        graph.edges()[e]["load"] = 0
    # adding the return edges
    # for e in graph.edges():

        if not graph.has_edge(e[1], e[0]):
            graph.add_edge(e[1], e[0], capacity=0, load=0, tmp=True)

    # initialize source node
    s["dist"] = len(graph.nodes())

    # populate edges going out of the source node
    for e in graph.out_edges(source_node):
        graph.edges()[e]["load"] = graph.edges()[e]["capacity"]
        graph.nodes()[e[1]]["overrun"] = graph.edges()[e]["load"]
        graph.edges()[(e[1], e[0])]["load"] = -graph.edges()[e]["capacity"]

    # solve the max flow problem
    while has_active_node(graph, source_node, target_node):
        node = get_active_node(graph, source_node, target_node)
        if not push(graph, node):
            relabel(graph, node)
            print("** relabeling %s to dist %i" % (str(node), graph.nodes()[node]["dist"]))

    path = "./pkl"
    if not os.path.exists(path):
        os.makedirs(path)

    # save graph
    pickle.dump(graph, open(f"./pkl/graph_{str(source_node)}_{str(target_node)}_{str(graph.number_of_nodes())}_{str(graph.number_of_edges())}.pkl","wb"))

    # cleanup
    for edge in graph.edges():
        if hasattr(edge, "tmp"):
            graph.remove_edge(edge)

    # save graph after removing edge
    pickle.dump(graph, open(f"./pkl/graph_{str(source_node)}_{str(target_node)}_{str(graph.number_of_nodes())}_{str(graph.number_of_edges())}.pkl","wb"))

    # total flow from source:
    print(f"total flow from source: {graph.nodes()[source_node]}")

    # total flow to target:
    print(f"total flow to target: {graph.nodes()[target_node]}")


if __name__ == '__main__':
    push_and_relabel()