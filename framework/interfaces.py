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
class Connector:
    """
    This class is to setup a connection to databases
    To be implemented within packages for `Database Manager`
    """

    def __init__(self, params):
        """
        constructing a connection to databases
        :param params: dictionary with fields for specifying database server, username, password, etc., in the following
        format
               {
                    "host": address of the database server,
                    "user": username
                    "pwd": password
                    ...
               }
        """
        self.params = params
        pass


class DataManager:
    """
    This class provides functions for managing in and retrieving data from databases
    To be implemented within packages for `Database Manager`
    """

    def __init__(self, connector, params=None):
        """
        construct a data manager that makes use of the `connection` for working with databases
        :param connector:
        :param params: dictionary with fields for specifying, e.t., limitations for each data saving request, in the
            following format
                {
                    "key": explanation for the value
                    ...
                }
        """
        self.connector = connector
        self.params = params
        pass

    def search_networks(self, networks=None):
        """
        get information about a list of nodes from a network
        :param networks: list of string, each is a network identifier, if None then return all networks
        :return: dictionary that contains in the following format
                {
                    "found": list of dictionaries, each for a found network, in the following format
                            {
                                "id": id of the network
                                "properties": dictionary that contains properties of the node, in the following format
                                            {
                                                "name": name of the network
                                                "num_nodes": number of nodes
                                                "num_edges": number of edges
                                                "edge_types": list of string, each is a type of edge
                                                "node_types": list of string, each is a type of node
                                            }
                            }
                    "not_found": list of input node ids that are not found in the network
                }
        """

    def save_nodes(self, nodes, network, params=None):
        """
        add or update information for a list of edges in a network
        :param nodes: list dictionaries, each contains information about a node to be added/ updated, in the
            following format:
                {
                    "id": id of the node,
                    "name": name of the node
                    "type": type of the node
                    "community": optional, list of communities of the nodes by different algorithms, in the following
                        format
                        {
                            "algorithm": name of the algorithm used to discover the communities
                            "run_id": id of the run that discovered the communities, we need to save this information as
                             we will run the algorithms multiple times according to updates from partners
                            "membership": dictionary that contains information about communities of the node, in the
                                following format
                                {
                                    "community_id": id of the community
                                    "membership": a number denoting the membership of the node in the community
                                }
                        }
                    "centrality": optional, list of centrality measures of the nodes by different algorithms, in the
                        following
                        format
                        {
                            "algorithm": name of the algorithm used to compute the centrality
                            "run_id": id of the run that compute the centrality
                            "score": centrality score
                        }
                    "embedding": optional, list of embedding vectors of the nodes by different algorithms, in the
                        following format
                        {
                            "algorithm": name of the algorithm used to learn the embedding vector
                            "run_id": id of the run that learned the vector
                            "dimension": dimension of the vector
                            "vector": the vector
                        }
                    ...
                }
        :param network: a string to identify a unique network
        :param params: dictionary containing options for saving the nodes, in the following format
                {
                    "create_node": optional, True to create node if not exist, False otherwise,
                    ...
                }
        :return: sub-list of the input list that consists of nodes that cannot be added/ updated
        """
        pass

    def save_edges(self, edges, network, params=None):
        """
        create or update information for a list of edges in a network
        :param edges: list of dictionaries, each contains information about an edge to be created/ updated, in the
            following format:
                {
                    "source": id of source node,
                    "target": id of target node,
                            {
                                "observed": True if the edge is observed in data, False otherwise (e.g., the edge is inferred by
                                            latent link detection algorithms)
                                "inference": optional, dictionary that contains information about the inference of the edge if it
                                            is inferred one (i.e., when "observed" = False), in the following format
                                "algorithm": name of the algorithm used to infer the edge
                                "run_id": id of the run that inferred the edge
                            }
                    "properties": dictionaries containing properties of the edge, in the following format
                            {
                                "type": type of the edge, e.g., "work for", or "friend of",
                                "weight": optional, weight of the edge,
                                "confidence": optional, confidence/certainty of the edge,
                                ...
                            }
                    ...
                }
        :param network: a string to identify a unique network
        :param params: dictionary containing options for saving the edges, in the following format
                {
                    "create_edge": optional, True to create edge if not exist, False otherwise,
                    "create_node": optional, True to create node if not exist, False otherwise,
                    ...
                }

        :return: sub-list of the input list that consists of edges that cannot be created/ updated

        """
        pass

    def delete_node(self, node_ids, network):
        """
        delete a list of nodes and their adjacent edges from a network
        :param node_ids: list of node ids
        :param network: a string to identify a unique network
        :return:  sub-list of the input list that consists of nodes that cannot be deleted
        """
        pass

    def delete_edges(self, edges, network):
        """
        delete a list of edges from a network
        :param edges: list of dictionaries, each contain information about an edge, in the format
            {
                "source": id of the source node
                "target": id of the target node
            }
        :param network: a string to identify a unique network
        :return:  sub-list of the input list that consists of edges that cannot be deleted
        """
        pass

    def get_network(self, network, node_ids=None, params=None):
        """
        get network or sub-network induced by a list of nodes
        :param network: a string to identify a unique network
        :param node_ids: list of the nodes' id, if `None` then return the whole network
        :param params: dictionary that contains criteria to select nodes, edges, and their associated information,
                if `None` means ``select all", in the following format
                {
                    "edge_types": list of selected edge types (, e.g., "work for" or "friend of")
                    "min_weight": minimum weight
                    "min_confidence": minimum confidence
                    ...
                }
        :return: dictionary that contains the list of edges in the (sub-) network and information of its nodes
                {
                    "edges": list of dictionaries, each contains selected information about an edge, each in the
                        following format
                            {
                                "source": id of source node,
                                "target": id of target node,
                                "properties": dictionary that contains properties of the edge, in the following format
                                            {
                                                "observed": True if the edge is observed in data, False otherwise
                                                (e.g., the edge is inferred by latent link detection algorithms)
                                                "weight": optional, weight of the edge
                                                "type": type of the edge, e.g., "work for", or "friend of",
                                                "confidence": optional, confidence/certainty of the edge
                                                ...
                                            }
                                ...
                            }
                    "nodes": list of dictionaries, each contains information about a node, each in the following format
                            {
                                "id": id of the node
                                "properties": dictionary that contains properties of the node, in the following format
                                            {
                                                "type": type of the node
                                                "name": name of the node
                                                ...
                                            }
                                ...
                            }
                }
        """
        pass

    def dump_network(self, network, output_dir, params=None):
        """
        dump the whole network to a specified directory
        :param network: a string to identify a unique network
        :param output_dir: directory to dump the network to
        :param params: dictionary that contains criteria to select nodes, edges, and their associated information,
            `None` means ``select all", in the following format
                {
                    "edge_types": list of selected edge types
                    "min_weight": optional, minimum weight
                    "min_confidence": optional, minimum confidence
                    ...
                    "output_format": optional, format of the dump files, e.g., edge list or adjacent list, etc.
                    "compressed": optional, to compress the dump files or not
                    ...
                }
        :return: 1 if the network is dumped successfully, or 0 otherwise
        """
        pass

    def get_neighbors(self, node_ids, network, params=None):
        """
        get neighbors of a list of nodes in a network
        :param node_ids: list of the node ids
        :param network: a string to identify a unique network
        :param params: dictionary that contains criteria to select neighbors, if `None` means ``select all", in the
                following format
                {
                    "node_types": list of selected node types
                    "min_weight": minimum weight
                    "min_confidence": minimum confidence
                    ...
                }
        :return: dictionary that contains the list of nodes and their neighbors
                {
                    "found": list of dictionaries, each contains information about neighbors of a node that can be
                        found in network, in the following format
                            {
                                "id": id of the node
                                "neighbors": list of dictionaries, each contains information about a neighbor, in the
                                    following format
                                        {
                                            "neighbor_id": id of the neighbor node
                                            "properties": dictionary contains information about properties of the neighbor,
                                                in the following format
                                                        {
                                                            "name": name of the neighbor node
                                                            "type": type of the neighbor node
                                                        }
                                            "edges": list of dictionaries, each contains information of an edge between
                                                the node and the neighbor, each in the following format
                                                        {
                                                            "observed": True if the edge is observed in data,
                                                                        False otherwise
                                                            "weight": optional, weight of the edge
                                                            "type": type of the edge, e.g., "work for", or "friend of"
                                                            "confidence": optional, confidence/certainty of the edge
                                                            ...
                                                        }
                                            ...
                                        }
                            }
                    "not_found": list of input node ids that are not found in the network
                }
        """
        pass

    def search_nodes(self, node_ids, network, params=None):
        """
        get information about a list of nodes from a network
        :param node_ids: list of node ids
        :param network: a string to identify a unique network
        :param params: list of properties associated with the nodes, e.g., "name", "type", "community",
            "centrality", "embedding", etc.
        :return: dictionary that contains in the following format
                {
                    "found": list of dictionaries, each for a found node, in the following format
                            {
                                "id": id of the node
                                "properties": dictionary that contains properties of the node, in the following format
                                            {
                                                "key": value, where "key" is a property in `params`, `value` is the
                                                        corresponding value of the node for that property, if the node
                                                        has,or `None` otherwise
                                            }
                            }
                    "not_found": list of input node ids that are not found in the network
                }
        """
        pass


class AnalysisRequester:
    """
    This class provides for requesting to perform analysis on some networks
    To be implemented by within packages for `Analyzer`
    """

    def __init__(self):
        pass

    def perform_analysis(self, task, params):
        """
        request to perform an analysis task
        :param task: dictionary that contains information about a requested task, in the following format
            {
                "task_id": id of the task, e.g., "community_detection", "link_detection", "node_matching", "embedding"
                "network": either: a string to identify the in-database network to perform the task on, or
                           a network in format of edge list, i.e., a list of dictionaries, each contains information
                            about an edge, each in the following format
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
                "options:" dictionary that contains algorithm/method selection and its parameters to perform the task,
                    in the following format
                    {
                        "method": one of predefined methods corresponding to the "task_id"
                        "parameters": dictionary that contains information about predefined parameters for the selected
                            method
                    }
                "run_id": id for the run
            }
            the list of task_ids, the algorithms/methods for the tasks and their parameters will be described in another
            document
        :param params: dictionary that contain other options for the task, in the following format
            {
                "run_id": id of the run
                "save_db": database manager that can be utilized for saving the task result
                "output_directory": (optional) directory to save the task result to files
                "compressed": (optional) to compress the output files or not
            }
        :return: 1 if the task is performed successfully, or 0 otherwise
        """
        pass
