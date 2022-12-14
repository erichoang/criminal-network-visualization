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
import sys
import os
import networkx as nx

# find path to root directory of the project so as to import from other packages
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

import analyzer.common.helpers as helpers


def pagerank(network, params):
    """
    wrapper for NetworkX's parerank function
    :param network:
    :param params:

    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_directed_graph(network)
        # print(graph)
        # print(node_ids)
        pr = nx.pagerank(graph)
        scores = [(node_ids[i], pr[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result


def authority(network, params):
    """
    wrapper for NetworkX's hits function
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_directed_graph(network)
        # print(graph)
        # print(node_ids)
        _, a = nx.hits(graph)
        scores = [(node_ids[i], a[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result


def betweenness(network, params):
    """
    wrapper for NetworkX's betweeness_centrality function
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }

    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)  # TODO: to be refactor
        # print(graph)
        # print(node_ids)
        centralities = nx.betweenness_centrality(graph)
        scores = [(node_ids[i], centralities[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result


def katz_centrality(network, params):
    """
    wrapper for NetworkX's katz_centrality function
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }

    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)  # TODO: to be refactor
        # print(graph)
        # print(node_ids)
        centralities = nx.katz_centrality(graph)
        scores = [(node_ids[i], centralities[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result


def closeness_centrality(network, params):
    """
    wrapper for NetworkX's closeness_centrality function
    :param network:
    :param params:
     :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }

    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)  # TODO: to be refactor
        # print(graph)
        # print(node_ids)
        centralities = nx.katz_centrality(graph)
        scores = [(node_ids[i], centralities[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result


def get_info():
    """
    get information about methods provided in this class
    :return: dictionary: Provides the name of the analysis task, available methods and information
                         about an methods parameter. Also provides full names of tasks, methods and parameter.
                         Information is provided in the following format:

                        {
                            'name': Full analysis task name as string
                            'methods': {
                                key: Internal method name (eg. 'asyn_lpa')
                                value: {
                                    'name': Full method name as string
                                    'parameter': {
                                        key: Parameter name
                                        value: {
                                            'description': Description of the parameter
                                            'fixed_options': {
                                                key: Accepted parameter value
                                                value: Full parameter value name as string
                                                !! If accepted values are integers key and value is 'Integer'. !!
                                            }
                                        }
                                    }
                                }
                            }
                        }
    """
    info = {'name': 'Social Influence Analysis',
            'methods': {
                'pagerank': {
                    'name': 'Pagerank',
                    'parameter': {}
                },
                'authority': {
                    'name': 'Authority',
                    'parameter': {}
                },
                'betweenness': {
                    'name': 'Betweeness Centrality',
                    'parameter': {}
                },
                'closeness_centrality': {
                    'name': 'Closeness Centrality',
                    'parameter': {}
                }
            }
            }
    return info


class SocialInfluenceAnalyzer:
    """
    class for performing community detection
    """

    def __init__(self, algorithm):
        """
        init a community detector using the given `algorithm`
        :param algorithm:
        """
        self.algorithm = algorithm
        self.methods = {
            'pagerank': pagerank,
            'authority': authority,
            'betweenness': betweenness,
            'katz_centrality': katz_centrality,
            'closeness_centrality': closeness_centrality
            # TODO: to add more methods from networkx, snap, and sklearn
        }

    def perform(self, network, params):
        """
        performing
        :param network:
        :param params:
        :return:
        """
        return self.methods[self.algorithm](network, params)
