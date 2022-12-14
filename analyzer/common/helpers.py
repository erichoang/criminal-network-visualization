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
import networkx as nx
from scipy.sparse import csr_matrix

def is_valid(edge, params):
    """
    to check if the input edge satisfies the conditions in params
    :param edge: dictionary contain information about an edge, in following format
                    {
                        "source": id of source node,
                        "target": id of target node,
                        "observed": True if the edge is observed in data, False otherwise (e.g., the edge is
                            inferred by latent link detection algorithms)
                        "properties": dictionary that contains properties of the edge, in the following format
                                    {
                                        "weight": optional, weight of the edge
                                        "type": type of the edge, e.g., "work for", or "friend of",
                                        "confidence": optional, confidence/certainty of the edge
                                        ...
                                    }
                        ...
                    }
    :param params: options for filtering edges
    :return:
    """
    # TODO: implement the condition checker
    return True


def get_edges_and_node_ids(network, params):
    nodes = {}
    edges = []
    node_ids = []

    network_edges = network.get('edges')

    for e in network_edges:
        if is_valid(e, params):
            source = e['source']
            target = e['target']
            if source not in nodes:
                source_index = len(node_ids)
                nodes[source] = source_index
                node_ids.append(source)
            else:
                source_index = nodes[source]

            if target not in nodes:
                target_index = len(node_ids)
                nodes[target] = target_index
                node_ids.append(target)
            else:
                target_index = nodes[target]

            edges.append((source_index, target_index))

    return edges, node_ids


def convert_to_nx_undirected_graph(network, params=None):
    """
    convert a undirected network in edge list format into `networkx` network
    :param network: is a dictionany having two keys 'edges' and 'nodes', 
                        value of key 'edges' is list of dictionaries, each contains selected information about an edge, 
                        each in the following format
                            {
                                "source": id of source node,
                                "target": id of target node,
                                "observed": True if the edge is observed in data, False otherwise (e.g., the edge is
                                    inferred by latent link detection algorithms)
                                "properties": dictionary that contains properties of the edge, in the following format
                                            {
                                                "weight": optional, weight of the edge
                                                "type": type of the edge, e.g., "work for", or "friend of",
                                                "confidence": optional, confidence/certainty of the edge
                                                ...
                                            }
                                ...
                            }
    :param params: options for filtering edges #TODO: to add options
    :return: (nx_network, node_ids)
        nx_network: networkx network with nodes indexed to 0, 1, etc
        node_ids: ids of nodes in input network, i.e., node_ids[i] is original id node i of nx_network
    """
    edges, node_ids = get_edges_and_node_ids(network, params)

    graph = nx.Graph()
    graph.add_edges_from(edges)
    return graph, node_ids


def convert_to_nx_directed_graph(network, params=None):
    """
    convert a directed network in edge list format into `networkx` network
    :param network: is a dictionany having two keys 'edges' and 'nodes', 
                        value of key 'edges' is list of dictionaries, each contains selected information about an edge, 
                        each in the following format
                            {
                                "source": id of source node,
                                "target": id of target node,
                                "observed": True if the edge is observed in data, False otherwise (e.g., the edge is
                                    inferred by latent link detection algorithms)
                                "properties": dictionary that contains properties of the edge, in the following format
                                            {
                                                "weight": optional, weight of the edge
                                                "type": type of the edge, e.g., "work for", or "friend of",
                                                "confidence": optional, confidence/certainty of the edge
                                                ...
                                            }
                                ...
                            }
    :param params: options for filtering edges #TODO: to add options
    :return: (nx_network, node_ids)
        nx_network: networkx network with nodes indexed to 0, 1, etc
        node_ids: ids of nodes in input network, i.e., node_ids[i] is original id node i of nx_network
    """
    edges, node_ids = get_edges_and_node_ids(network, params)

    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    return graph, node_ids

def convert_to_csr_sparse_matrix(network, params=None):
    """
    convert a network in edge list format into scipy  csr_sparse matrix
    :param network: is a dictionany having two keys 'edges' and 'nodes', 
                        value of key 'edges' is list of dictionaries, each contains selected information about an edge, 
                        each in the following format
                            {
                                "source": id of source node,
                                "target": id of target node,
                                "observed": True if the edge is observed in data, False otherwise (e.g., the edge is
                                    inferred by latent link detection algorithms)
                                "properties": dictionary that contains properties of the edge, in the following format
                                            {
                                                "weight": optional, weight of the edge
                                                "type": type of the edge, e.g., "work for", or "friend of",
                                                "confidence": optional, confidence/certainty of the edge
                                                ...
                                            }
                                ...
                            }
    :param params: options for filtering edges #TODO: to add options
    :return: (nx_network, node_ids)
        matrix: scipy csr_sparse matrix
        node_ids: ids of nodes in input matrix, i.e., node_ids[i] is original id node i of nx_network
    """
    nodes = {}
    node_ids = []
    rows = []
    cols = []
    weights = []

    network_edges = network.get('edges')

    for e in network_edges:
        if is_valid(e, params):
            source = e['source']
            target = e['target']
            if 'weight' in e['properties']:
                weight = e['properties']['weight']
            else:
                weight = 1.0
            if source not in nodes:
                source_index = len(node_ids)
                nodes[source] = source_index
                node_ids.append(source)
            else:
                source_index = nodes[source]

            if target not in nodes:
                target_index = len(node_ids)
                nodes[target] = target_index
                node_ids.append(target)
            else:
                target_index = nodes[target]
            rows.append(source_index)
            cols.append(target_index)
            weights.append(weight)

    matrix = csr_matrix((weights, (rows, cols)))
    matrix = matrix.asfptype()
    return matrix, node_ids
