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
import itertools
import networkx.algorithms.community as methods
import networkx
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering

# find path to root directory of the project so as to import from other packages
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

import analyzer.common.helpers as helpers


def _generate_communities_and_membership(nx_communities, node_ids):
    communities = []
    membership = {}
    for c in range(len(nx_communities)):
        for u in nx_communities[c]:
            nid = node_ids[u]
            if nid in membership:
                membership[nid][c] = 1.0
            else:
                membership[nid] = {c: 1.0}
        communities.append(dict([(node_ids[u], 1.0) for u in nx_communities[c]]))
    return communities, membership


def k_clique_communities(network, params):
    """
    wrapper for NetworkX's k_clique_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        # If no parameter were given, use 3 as default.
        # May not be the most elegant solution but is the easiest for now.
        try:
            k = params['K']
        except KeyError:
            k = 3
        nx_comms = list(methods.k_clique_communities(graph, k))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result


def greedy_modularity_communities(network, params):
    """
    wrapper for NetworkX's greedy_modularity_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        nx_comms = list(methods.greedy_modularity_communities(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result


def asyn_lpa_communities(network, params):
    """
    wrapper for NetworkX's asynchronous label propagation algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_directed_graph(network)
        nx_comms = list(methods.asyn_lpa_communities(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result


def label_propagation_communities(network, params):
    """
    wrapper for NetworkX's semi-synchronous label propagation algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        nx_comms = list(methods.label_propagation_communities(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result


def kernighan_lin_bipartition(network, params):
    """
    wrapper for NetworkX's Kernighan–Lin bipartition algorithm to partition a graph into two blocks
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        nx_comms = list(methods.kernighan_lin_bisection(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result


def spectral_communities(network, params):
    """
    wrapper for NetworkX's k_clique_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        # If no parameter were given, use 3 as default.
        # May not be the most elegant solution but is the easiest for now.
        try:
            k = params['K']
        except KeyError:
            k = 3

        adj_matrix = networkx.adjacency_matrix(graph)
        clustering = SpectralClustering(n_clusters=k, assign_labels="discretize", random_state=0).fit(adj_matrix)
        # print(clustering.labels_)
        communities = [{}] * k
        membership = {}
        for u in range(len(clustering.labels_)):
            c = clustering.labels_[u]
            nid = node_ids[u]
            if nid in membership:
                membership[nid][c] = 1.0
            else:
                membership[nid] = {c: 1.0}
            communities[c][nid] = 1.0

        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result

    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result


def hierarchical_communities(network, params):
    """
    wrapper for NetworkX's k_clique_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        # If no parameter were given, use 3 as default.
        # May not be the most elegant solution but is the easiest for now.
        try:
            k = params['K']
        except KeyError:
            k = 3
        adj_matrix = networkx.adjacency_matrix(graph)
        clustering = AgglomerativeClustering(n_clusters=k).fit(adj_matrix.toarray())
        # print(clustering.labels_)
        communities = [{}] * k
        membership = {}
        for u in range(len(clustering.labels_)):
            c = clustering.labels_[u]
            nid = node_ids[u]
            if nid in membership:
                membership[nid][c] = 1.0
            else:
                membership[nid] = {c: 1.0}
            communities[c][nid] = 1.0

        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
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
                                            'options': {
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
    info = {'name': 'Community Detection',
            'methods': {
                'k_cliques': {
                    'name': 'K-clique',
                    'parameter': {
                        'K': {
                            'description': 'Size of smallest clique.',
                            'options': {'Integer': [3, 4, 5, 6, 7]}
                        }
                    }
                },
                'modularity': {
                    'name': 'Modularity Maximization',
                    'parameter': {}
                },
                'label_propagation': {
                    'name': 'Label Propagation',
                    'parameter': {}
                },
                'asyn_lpa': {
                    'name': 'Asynchronous Label Propagation',
                    'parameter': {}
                },
                'bipartition': {
                    'name': 'Kernighan–Lin Bipartition',
                    'parameter': {}
                },
                'spectral': {
                    'name': 'Spectral clustering',
                    'parameter': {
                        'K': {
                            'description': 'number of communities',
                            'options': {'Integer': [3, 4, 5, 6, 7]}
                        }
                    }
                },
                'hierarchical': {
                    'name': 'Hierarchical clustering',
                    'parameter': {
                        'K': {
                            'description': 'number of communities',
                            'options': {'Integer': [3, 4, 5, 6, 7]}
                        }
                    }
                }
            }
            }
    return info


class CommunityDetector:
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
            'k_cliques': k_clique_communities,
            'modularity': greedy_modularity_communities,
            'asyn_lpa': asyn_lpa_communities,
            'label_propagation': label_propagation_communities,
            'bipartition': kernighan_lin_bipartition,
            'spectral': spectral_communities,
            'hierarchical': hierarchical_communities
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
