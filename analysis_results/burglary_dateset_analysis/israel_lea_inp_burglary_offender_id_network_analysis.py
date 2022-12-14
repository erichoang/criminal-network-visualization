"""
=================================== LICENSE ==================================
Copyright (c) 2021, Consortium Board ROXANNE
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of the ROXANNE nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY CONSORTIUM BOARD ROXANNE ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CONSORTIUM BOARD TENCOMPETENCE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
==============================================================================
"""
import os
import sys
import getopt
import time
import pickle
import json
import operator
import random
import pandas as pd
import networkx as nx
import networkx.algorithms.link_prediction as lp_methods

from networkx.readwrite import json_graph
from copy import deepcopy
from joblib import Parallel, delayed

tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-3])
if path2root not in sys.path:
    sys.path.append(path2root)

from analyzer import link_prediction

LIST_TOP_K = [10, 20, 50, 100, 200]

def load_graph_from_json_file(graph_file_path):
    with open(graph_file_path) as json_file:
        data = json.load(json_file)
    G = json_graph.node_link_graph(data)
    return G

def dump_centrality_scores(graph, dump_path):
    scores = nx.betweenness_centrality(graph, weight='weight')
    with open(dump_path, 'wb') as fp:
        pickle.dump(scores, fp)
    print('Dumped file succesful: ' +  dump_path)

def get_top_k_central_nodes(scores, top_k=100):
    cd = sorted(scores.items(),key=operator.itemgetter(1),reverse=True)
    list_tuple_score_node = cd[:top_k]
    return list_tuple_score_node

def select_top_k(candidates, top_k=3):
    candidates.sort(key=operator.itemgetter(1), reverse=True)
    return [u[0] for u in candidates[:top_k]]

def generate_link_predictions(scores, sources, top_k=3):
    preds = dict()
    for u in sources:
        preds[u] = []

    for u, v, p in scores:
        preds[u].append((v, p))
    
    for u in preds:
        preds[u] = select_top_k(preds[u], top_k)

    return preds

def get_top_k_predicted_links(nx_undirected_graph, source_nodes, top_k=3):
    undirected_graph = nx_undirected_graph
    candidate_links = link_prediction._get_candidates(undirected_graph, source_nodes)
    print('length of candidate_links:', len(candidate_links))
    lp_scores = lp_methods.jaccard_coefficient(undirected_graph, candidate_links)
    predictions = generate_link_predictions(lp_scores, sources=source_nodes, top_k=top_k)

    return predictions

def has_two_hop_neighbors(nx_undirected_graph, node):
    neighbors = nx_undirected_graph.neighbors(node)
    second_hop_neighbors = set()

    for v in neighbors:
        second_hop_neighbors = second_hop_neighbors.union(set(nx_undirected_graph.neighbors(v)))
    second_hop_neighbors = second_hop_neighbors.difference(neighbors)

    if node in second_hop_neighbors:
        second_hop_neighbors.remove(node)
    
    if len(second_hop_neighbors) > 0:
        return True
    else:
        return False 

def run_link_predictions(nx_undirected_graph, removed_edge):
    result = dict()

    source, target = removed_edge
    temp_graph = deepcopy(nx_undirected_graph)
    temp_graph.remove_edge(source, target)

    pred_links = get_top_k_predicted_links(temp_graph, source_nodes=[source], top_k=5)
    # print(pred_links)

    result[removed_edge] = {
        'top_5': target in pred_links[source],
        'top_3': target in pred_links[source][:3],
        'top_1': target in pred_links[source][:1],
    }
    # print(result, pred_links)

    return result

def run_link_predictions_with_multi_edges(nx_undirected_graph, list_removed_edge):
    result = dict()

    temp_graph = deepcopy(nx_undirected_graph)
    set_source_node = set()
    for removed_edge in list_removed_edge:
        source, target = removed_edge
        set_source_node.add(source)
        set_source_node.add(target)

        if removed_edge in temp_graph.edges():
            temp_graph.remove_edge(source, target)
    
    list_source_node = list(set_source_node)
    print(nx.info(temp_graph))
    # print('List of source node', list_source_node)

    pred_links = get_top_k_predicted_links(temp_graph, source_nodes=list_source_node, top_k=5)
    # print(pred_links)

    for removed_edge in list_removed_edge:
        source, target = removed_edge
        result[removed_edge] = {
            'top_5': target in pred_links[source] or source in pred_links[target],
            'top_3': target in pred_links[source][:3] or source in pred_links[target][:3],
            'top_1': target in pred_links[source][:1] or source in pred_links[target][:1]
        }
    # print(result, pred_links)

    return result

def run_link_predictions_with_multi_edges_ground_truth(nx_undirected_graph, list_removed_edge):
    result = dict()

    temp_graph = deepcopy(nx_undirected_graph)
    set_source_node = set()
    for removed_edge in list_removed_edge:
        source, target = removed_edge
        set_source_node.add(source)
        set_source_node.add(target)

    list_source_node = list(set_source_node)
    print(nx.info(nx_undirected_graph))
    # print('List of source node', list_source_node)

    pred_links = get_top_k_predicted_links(temp_graph, source_nodes=list_source_node, top_k=5)
    print(pred_links)

    for removed_edge in list_removed_edge:
        source, target = removed_edge
        result[removed_edge] = {
            'top_5': target in pred_links[source] or source in pred_links[target],
            'top_3': target in pred_links[source][:3] or source in pred_links[target][:3],
            'top_1': target in pred_links[source][:1] or source in pred_links[target][:1]
        }

    # print(result, pred_links)

    return result

def calculate_accuaracy(list_item):
    return (sum(list_item) / len(list_item)) * 100

def evaluate_results(dict_results):
    list_value_top_1 = []
    list_value_top_3 = []
    list_value_top_5 = []
    for _, value in dict_results.items():
        list_value_top_1.append(value['top_1'])
        list_value_top_3.append(value['top_3'])
        list_value_top_5.append(value['top_5'])
    
    acc_top_1 = round(calculate_accuaracy(list_value_top_1), 4)
    acc_top_3 = round(calculate_accuaracy(list_value_top_3), 4)
    acc_top_5 = round(calculate_accuaracy(list_value_top_5), 4)
    
    print('top_1:', round(calculate_accuaracy(list_value_top_1), 4))
    print('top_3:', round(calculate_accuaracy(list_value_top_3), 4))
    print('top_5:', round(calculate_accuaracy(list_value_top_5), 4))

    return (acc_top_1, acc_top_3, acc_top_5)

def get_run_version():
    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]
    
    # Options
    options = "hmr:"
    
    # Long options
    long_options = ["Help", "My_file", "Run"]
    
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        # checking each argument
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-h", "--Help"):
                print ("Displaying Help")
                
            elif currentArgument in ("-m", "--My_file"):
                print ("Displaying file_name:", sys.argv[0])
                
            elif currentArgument in ("-r", "--Run"):
                print (("Execute the run (% s)") % (currentValue))
                return currentValue
             
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

def run_experiment_top_k_central_node(graph_file_path, nx_undirected_graph, scores_centrality):
    undirected_graph = nx_undirected_graph

    pd_data = []
    for top_k in LIST_TOP_K:
        print('Number of Central Nodes:', top_k, 'Running Version:', run_version)

        central_nodes = get_top_k_central_nodes(scores_centrality, top_k=top_k)

        source_nodes = []
        for node, value in central_nodes:
            source_nodes.append(node)
        print(source_nodes)

        removed_edges = set()
        for source_node in source_nodes:
            for u, v in undirected_graph.edges(source_node):
                if u != source_node:
                    removed_edges.add((source_node, u))
                
                if v != source_node:
                    removed_edges.add((source_node, v))
        print('Number of removed links:', len(removed_edges))
        
        results = Parallel(n_jobs=10, backend='multiprocessing')(
            delayed(run_link_predictions)
            (undirected_graph, removed_edge) for removed_edge in removed_edges
        )

        dict_results = dict()
        for result in results:
            for edge, value in result.items():
                if edge not in dict_results.keys():
                    dict_results[edge] = value
                else:
                    print('Duplicated value:', dict_results, edge, value)
        print(dict_results)

        acc_top_1, acc_top_3, acc_top_5 = evaluate_results(dict_results)

        row = (top_k, len(removed_edges), acc_top_1, acc_top_3, acc_top_5)
        pd_data.append(row)

    df = pd.DataFrame(pd_data, columns=['#_central_nodes', '#_removed_edges',
                                        'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    df_file_path = 'analysis_results/burglary_dateset_analysis/' + 'df_' + graph_file_path.split('.')[0].split('/')[2] + \
                    '_undirected_betweenness_centrality_scores' + '_v' + run_version + '.csv'
    df.to_csv(df_file_path)
    print('Dumped:', df_file_path)

def run_experiment_on_removing_random_edges(graph_file_path, nx_undirected_graph, percent_removed_edges=0.01):
    undirected_graph = nx_undirected_graph

    removed_edges = random.sample(undirected_graph.edges(), int(round(percent_removed_edges * len(undirected_graph.edges()), 0)))
    print('Number of removed links:', len(removed_edges))

    results = run_link_predictions_with_multi_edges(undirected_graph, removed_edges)
    print(results)


    acc_top_1, acc_top_3, acc_top_5 = evaluate_results(results)

    pd_data = []
    row = (len(removed_edges), acc_top_1, acc_top_3, acc_top_5)
    pd_data.append(row)

    df = pd.DataFrame(pd_data, columns=['#_removed_edges', 'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    df_file_path = 'analysis_results/burglary_dateset_analysis/' + 'df_' + graph_file_path.split('.')[0].split('/')[2] + \
                    '_removed_edges_' + str(int(percent_removed_edges*100)) + '%_v' + run_version + '.csv'
    df.to_csv(df_file_path)
    print('Dumped:', df_file_path)

def run_experiment_on_ground_truth_graph(graph_file_path, nx_undirected_graph, nx_undirected_graph_ground_truth):
    undirected_graph = nx_undirected_graph
    undirected_graph_ground_truth = nx_undirected_graph_ground_truth

    new_nodes = set(undirected_graph_ground_truth.nodes()).difference(set(undirected_graph.nodes()))

    new_edges = set()
    for edge in undirected_graph_ground_truth.edges():
        source, target = edge

        if (source, target) not in undirected_graph.edges() and (target, source) not in undirected_graph.edges():
            new_edges.add((source, target))

    # new_edges = set(undirected_graph_ground_truth.edges()).difference(set(undirected_graph.edges()))

    print('new nodes:', len(new_nodes))
    print('====================================================')
    print('new edges:', len(new_edges))

    # new_edges_in_new_nodes = set()
    # for new_edge in new_edges:
    #     source, target = new_edge
    #     if source in new_nodes or target in new_nodes:
    #         new_edges_in_new_nodes.add(new_edge)
    # print('====================================================')
    # print('new_edges_in_new_nodes:', len(new_edges_in_new_nodes))

    new_edges_in_existing_nodes = set()
    for new_edge in new_edges:
        source, target = new_edge
        if source not in new_nodes and target not in new_nodes:
            new_edges_in_existing_nodes.add((source, target))

    print('====================================================')
    print('new_edges_in_existing_nodes:', len(new_edges_in_existing_nodes))

    set_no_neighbor_nodes = set()
    set_edges_having_two_hop_neighbors = set()
    for new_edge in new_edges_in_existing_nodes:
        source, target = new_edge

        if len([n for n in undirected_graph.neighbors(source)]) == 0:
            set_no_neighbor_nodes.add(source)
            print(source)

        if len([n for n in undirected_graph.neighbors(target)]) == 0:
            set_no_neighbor_nodes.add(target)
            print(target)
        
        if has_two_hop_neighbors(undirected_graph, source) and has_two_hop_neighbors(undirected_graph, target):
            set_edges_having_two_hop_neighbors.add(new_edge)
    
    print('set_no_neighbor_nodes:', set_no_neighbor_nodes, len(set_no_neighbor_nodes))
    print('set_edges_having_two_hop_neighbors:', set_edges_having_two_hop_neighbors, len(set_edges_having_two_hop_neighbors))

    removed_edges = set_edges_having_two_hop_neighbors
    print('Number of removed links:', len(removed_edges))

    results = run_link_predictions_with_multi_edges_ground_truth(undirected_graph, removed_edges)
    # print(results)


    acc_top_1, acc_top_3, acc_top_5 = evaluate_results(results)

    pd_data = []
    row = (len(removed_edges), acc_top_1, acc_top_3, acc_top_5)
    pd_data.append(row)

    df = pd.DataFrame(pd_data, columns=['#_removed_edges', 'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    df_file_path = 'analysis_results/burglary_dateset_analysis/' + 'df_' + graph_file_path.split('.')[0].split('/')[2] + \
                    '_and_ground_truth_graph_' + 'v' + run_version + '.csv'
    df.to_csv(df_file_path)
    print('Dumped:', df_file_path)

if __name__ == "__main__":
    start = time.time()
    run_version = get_run_version()
    if run_version is None:
        run_version = str(0)
    # Opening JSON file
    # graph_file_path = 'datasets/preprocessed/locard_dataset_viewers_broadcasters_network.json'
    graph_file_path = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network.json'
    graph = load_graph_from_json_file(graph_file_path)
    undirected_graph = graph.to_undirected()
    print(nx.info(undirected_graph))

    # graph_by_date_file_path = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network_from_2010-01-01_to_2019-12-31.json'
    graph_by_date_file_path = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network_from_2010-01-01_to_2018-12-31.json'
    graph_by_date = load_graph_from_json_file(graph_by_date_file_path)
    undirected_graph_by_date = graph_by_date.to_undirected()
    print(nx.info(undirected_graph_by_date))


    # # nx.write_gpickle(G, 'datasets/nx_graphs/locard_dataset_viewers_broadcasters_network.gpickle')
    # G = nx.read_gpickle('datasets/nx_graphs/locard_dataset_viewers_broadcasters_network.gpickle')

    print(nx.info(graph))
    print(nx.info(undirected_graph))
    scores_centrality_file_path = 'analysis_results/burglary_dateset_analysis/' + graph_file_path.split('.')[0].split('/')[2] + \
                       '_undirected_betweenness_centrality_scores' + '.pickle'
    dump_centrality_scores(undirected_graph, scores_centrality_file_path)

    scores = nx.betweenness_centrality(G, weight='weight')
    with open('analysis_results/burglary_dateset_analysis/betweenness_centrality_scores_israel_lea_inp_burglary_offender_id_network.pickle', 'wb') as fp:
        pickle.dump(scores, fp)

    scores_centrality = pickle.load(open(scores_centrality_file_path, 'rb'))

    # run_experiment_top_k_central_node(graph_file_path, undirected_graph, scores_centrality)
    run_experiment_on_removing_random_edges(graph_file_path, undirected_graph, percent_removed_edges=0.01)
    # run_experiment_on_ground_truth_graph(graph_file_path=graph_by_date_file_path,
    #                                      nx_undirected_graph=undirected_graph_by_date,
    #                                      nx_undirected_graph_ground_truth=undirected_graph)

    end = time.time()
    print('{:.4f} s'.format(end-start))
