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
# helper functions for ROXANNE's first field test

import ast
import itertools
import networkx as nx
import numpy as np

import os
import sys

tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-2])
if path2root not in sys.path:
    sys.path.append(path2root)

print('fft_helpters: path2root = ', path2root)

if path2root not in sys.path:
    sys.path.append(path2root)
from storage.kit.VBx import diarization_lib
from storage.builtin_datasets import BuiltinDataset

def _generate_channels_and_index(wp5_outputs):
    channels = {}
    for con in wp5_outputs['conversations']:
        for channel in con['channels']:
            channels[channel['id']] = channel

    # build channel-2-index map
    channel2index = {}
    for con in wp5_outputs['conversations']:
        for channel in con['channels']:
            channel2index[channel['id']] = len(channel2index)
    
    return channels, channel2index

def _cluster_from_voice_prints_matrix(channel2index, wp5_outputs, threhold, calibration):
    # cluster
    voiceprintsMatrix = np.zeros((len(channel2index), len(channel2index)))
    for u, row in wp5_outputs['voiceprintsMatrix'].items():
        u_index = channel2index[u]
        for v, s in row.items():
            v_index = channel2index[v]
            voiceprintsMatrix[u_index, v_index] = s

    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        for s in channel_ids:
            for l in channel_ids:
                if s != l:
                    s_index = channel2index[s]
                    l_index = channel2index[l]
                    voiceprintsMatrix[s_index, l_index] = -np.inf

    if calibration:
        thr, scr_cal = diarization_lib.twoGMMcalib_lin(voiceprintsMatrix[np.where(np.isfinite(voiceprintsMatrix))])
    else:
        thr = 0
    labels = diarization_lib.AHC(voiceprintsMatrix, thr + threhold)

    return labels 

def _generate_nodes(channels, channel2index, labels):
    nodes = {}
    for channel in channels:
        index = channel2index[channel]
        channel_info = channels[channel]
        if 'transcription' in channel_info:
            del channel_info['transcription']  # ignore the transcription in first field test

        c = labels[index]

        if c in nodes:
            nodes[c].append(channel_info)
        else:
            nodes[c] = [channel_info]
    return nodes

def _generate_nodes_aegis(channels, channel2index, labels):
    nodes = {}
    for channel in channels:
        index = channel2index[channel]
        channel_info = channels[channel]
        if 'transcription' in channel_info:
            del channel_info['transcription']  # ignore the transcription in first field test

        c = labels[index]

        if c in nodes:
            nodes[c].append(channel_info)
        else:
            nodes[c] = [channel_info]
    return nodes

# def _generate_nodes_aegis(channels):
#     nodes = {}
#     for channel in channels:
#         channel_info = channels[channel]
#         if 'transcription' in channel_info:
#             del channel_info['transcription']  # ignore the transcription in first field test

#         node_id = channel_info['number']

#         nodes[node_id] = channel_info
    
#     return nodes

def _generate_edges(channel2index, labels, wp5_outputs, directed):
    edges = {}
    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        if 'date' in con:
            con_date = con['date']
        else:
            con_date = None
        # print(con_date)
        # print(channel_ids)
        for i in range(len(channel_ids)):
            s = channel_ids[i]
            for j in range(len(channel_ids)):
                if j == i:
                    continue
                l = channel_ids[j]
                if i < j or not directed:
                    s_cid = labels[channel2index[s]]
                    l_cid = labels[channel2index[l]]
                    if s_cid in edges:
                        if l_cid in edges[s_cid]:
                            edges[s_cid][l_cid]['weight'] += 1
                            if 'timestamps' in edges[s_cid][l_cid]:
                                temp_timestamps = edges[s_cid][l_cid]['timestamps']
                                temp_timestamps.append(con_date)
                                edges[s_cid][l_cid]['timestamps'] = temp_timestamps
                        else:
                            if con_date is not None:
                                edges[s_cid][l_cid] = {'weight' : 1, 'timestamps': [con_date]}
                            else:
                                edges[s_cid][l_cid] = {'weight' : 1}
                    else:
                        if con_date is not None:
                            edges[s_cid] = {l_cid: {'weight' : 1, 'timestamps': [con_date]}}
                        else:
                            edges[s_cid] = {l_cid: {'weight' : 1}}
    return edges

def _generate_edges_aegis(channel2index, labels, wp5_outputs, directed):
    edges = {}
    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        if 'date' in con:
            con_date = con['date']
        else:
            con_date = None
        print(con_date)
        print(channel_ids)
        for i in range(len(channel_ids)):
            s = channel_ids[i]
            for j in range(len(channel_ids)):
                if j == i:
                    continue
                l = channel_ids[j]
                if i < j or not directed:
                    s_cid = labels[channel2index[s]]
                    l_cid = labels[channel2index[l]]
                    # timestamp_val = (con_date, channel_ids)
                    timestamp_val = con_date
                    if s_cid in edges:
                        if l_cid in edges[s_cid]:
                            edges[s_cid][l_cid]['weight'] += 1
                            if 'timestamps' in edges[s_cid][l_cid]:
                                temp_timestamps = edges[s_cid][l_cid]['timestamps']
                                temp_timestamps = temp_timestamps.append(timestamp_val)
                                edges[s_cid][l_cid]['timestamps'] = temp_timestamps
                        else:
                            if con_date is not None:
                                edges[s_cid][l_cid] = {'weight' : 1, 'timestamps': [timestamp_val]}
                            else:
                                edges[s_cid][l_cid] = {'weight' : 1}
                    else:
                        if con_date is not None:
                            edges[s_cid] = {l_cid: {'weight' : 1, 'timestamps': [timestamp_val]}}
                        else:
                            edges[s_cid] = {l_cid: {'weight' : 1}}
    return edges


def _generate_phone_number_edges_aegis(wp5_outputs, directed):
    edges = {}

    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        channel_numbers = [channel['number'] for channel in con['channels']]

        if 'date' in con:
            con_date = con['date']
        else:
            con_date = None

        for i in range(len(channel_numbers)):
            s = channel_numbers[i]
            for j in range(len(channel_numbers)):
                if j == i:
                    continue
                l = channel_numbers[j]
                if i < j or not directed:
                    s_cid = s
                    l_cid = l
                    # timestamp_val = (con_date, channel_ids)
                    timestamp_val = con_date
                    if s_cid in edges:
                        if l_cid in edges[s_cid]:
                            edges[s_cid][l_cid]['weight'] += 1
                            if 'timestamps' in edges[s_cid][l_cid]:
                                temp_timestamps = edges[s_cid][l_cid]['timestamps']
                                temp_timestamps.append(timestamp_val)
                                edges[s_cid][l_cid]['timestamps'] = temp_timestamps
                        else:
                            if con_date is not None:
                                edges[s_cid][l_cid] = {'weight' : 1, 'timestamps': [timestamp_val]}
                            else:
                                edges[s_cid][l_cid] = {'weight' : 1}
                    else:
                        if con_date is not None:
                            edges[s_cid] = {l_cid: {'weight' : 1, 'timestamps': [timestamp_val]}}
                        else:
                            edges[s_cid] = {l_cid: {'weight' : 1}}
    return edges

def _construct_network(nodes, edges):
    network = []
    for node in nodes:
        network.append({'type': 'node',
                        'id': 'speaker_{}'.format(node),
                        'properties': {'type': 'cluster',
                                       'channels': nodes[node]}
                       })
                       
    for u in edges:
        for v in edges[u]:
            edge_properties = dict()
            edge_properties['type'] = 'conversations'
            edge_properties['weight'] = edges[u][v]['weight']
            if 'timestamps' in edges[u][v]:
                edge_properties['timestamps'] = edges[u][v]['timestamps']
            network.append({'type': 'edge',
                            'source': 'speaker_{}'.format(u),
                            'target': 'speaker_{}'.format(v),
                            'properties': edge_properties
                           })
    return network

def _construct_network_aegis(nodes, speaker_edges, phone_number_edges, directed):
    if directed == True:
        nx_graph = nx.DiGraph()
    else:
        nx_graph = nx.Graph()

    dict_node_phone_number = dict()
    for node in nodes:
        channels = nodes[node]

        phone_numbers = []
        for idx, channel in enumerate(channels):
            channel_info = channel
            # number = channel_info.pop('number', 'phone_number_{}'.format(node))
            number = channel_info['number']
            channels[idx] = channel_info
            phone_numbers.append(number)

        # print('phone_numbers:', phone_numbers)
        # print('channels:', channels)
        dict_node_phone_number[node] = phone_numbers
        # dict_node_phone_number[node] = list(set(phone_numbers))

        node_properties = {'type': 'cluster',
                           'channels': channels}

        nx_graph.add_node('speaker_{}'.format(node), type='node', properties=node_properties)
        
        for phone_number in phone_numbers:
            phone_node_properties = {'type': 'phone_number',
                                     'channels': channels}

            nx_graph.add_node(phone_number, type='node', properties=phone_node_properties)
            
    print(dict_node_phone_number)

    # for node in nx_graph.nodes(data=True):
    #     print(node)
        
    for u in speaker_edges:
        for v in speaker_edges[u]:
            timestamps = speaker_edges[u][v]['timestamps']
            # timestamps_no_channel_id = []
            # for timestamp in timestamps:
            #     date = timestamp[0]
            #     channel_id_1 = timestamp[1][0]
            #     channel_id_2 = timestamp[1][1]

            #     print(timestamp[0], timestamp[1][0], timestamp[1][1])

            u_phone_numbers = dict_node_phone_number[u]
            for u_phone_number in u_phone_numbers:
                temp_edge = ('speaker_{}'.format(u), u_phone_number)
                temp_edge_properties = {
                    'type': 'calling'
                }
                if temp_edge not in nx_graph.edges():
                    temp_edge_properties['weight'] = 1
                    temp_edge_properties['timestamps'] = timestamps
                    nx_graph.add_edge(temp_edge[0], temp_edge[1], type='edge', properties=temp_edge_properties)
                else:
                    temp_weight = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight']
                    temp_weight = temp_weight + 1
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight'] = temp_weight
                    temp_timestamps = [ts for ts in nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps']]
                    temp_timestamps = temp_timestamps + timestamps
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps'] = temp_timestamps
            
            v_phone_numbers = dict_node_phone_number[v]
            for v_phone_number in v_phone_numbers:
                temp_edge = (v_phone_number, 'speaker_{}'.format(v))
                temp_edge_properties = {
                    'type': 'receiving'
                }
                if temp_edge not in nx_graph.edges():
                    temp_edge_properties['weight'] = 1
                    temp_edge_properties['timestamps'] = timestamps
                    nx_graph.add_edge(temp_edge[0], temp_edge[1], type='edge', properties=temp_edge_properties)
                else:
                    temp_weight = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight']
                    temp_weight = temp_weight + 1
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight'] = temp_weight
                    temp_timestamps = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps']
                    temp_timestamps = temp_timestamps + timestamps
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps'] = temp_timestamps


    for u in phone_number_edges:
        for v in phone_number_edges[u]:
            temp_edge = (u, v)
            timestamps = phone_number_edges[u][v]['timestamps']
            temp_edge_properties = {
                    'type': 'conversations'
                }
            if temp_edge not in nx_graph.edges():
                temp_edge_properties['weight'] = phone_number_edges[u][v]['weight']
                temp_edge_properties['timestamps'] = phone_number_edges[u][v]['timestamps']
                nx_graph.add_edge(temp_edge[0], temp_edge[1], type='edge', properties=temp_edge_properties)
            else:
                temp_weight = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight']
                temp_weight = temp_weight + phone_number_edges[u][v]['weight']
                nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight'] = temp_weight
                temp_timestamps = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps']
                temp_timestamps.append(timestamps)
                nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps'] = temp_timestamps

    network = []
    for node_id, node_data in nx_graph.nodes(data=True):
        node = {
            'type': node_data['type'],
            'id': node_id,
            'properties': node_data['properties']
        }
        network.append(node)
    
    for source_id, target_id, edge_data in nx_graph.edges(data=True):
        edge = {
            'type': edge_data['type'],
            'source': source_id,
            'target': target_id,
            'properties': edge_data['properties']
        }
        network.append(edge)
        weight = edge_data['properties']['weight']
        if weight > 1:
            print(edge)


    # for edge in nx_graph.edges(data=True):
    #     u = edge[0]
    #     v = edge[1]
    #     # print(edge, nx_graph[u]['properties']['channels']['id'], nx_graph[v]['properties']['channels']['id'])
    #     print(edge)
    #     # print(nx_graph.nodes(data=True)[u]['properties']['channels'], nx_graph.nodes(data=True)[v]['properties']['channels'])


    # for u in edges:
    #     for v in edges[u]:
    #         print('nodes[v]', nodes[v])
    #         edge_properties = dict()
    #         edge_properties['type'] = 'conversations'
    #         u_v_weight = edges[u][v]['weight']
    #         edge_properties['weight'] = edges[u][v]['weight']

    #         timestamps = edges[u][v]['timestamps']
    #         print('timestamps', timestamps)
    #         for timestamp in timestamps:
    #             print(timestamp[0], timestamp[1][0], timestamp[1][1])


    #         if 'timestamps' in edges[u][v]:
    #             edge_properties['timestamps'] = edges[u][v]['timestamps']

    #         u_phone_numbers = dict_node_phone_number[u]
    #         # print(u, u_phone_numbers)
    #         for u_phone_number in u_phone_numbers:
    #             network.append({'type': 'edge',
    #                             'source': 'speaker_{}'.format(u),
    #                             'target': u_phone_number,
    #                             'properties': edge_properties
    #                         })         

    #         v_phone_numbers = dict_node_phone_number[v]
    #         # print(v, v_phone_numbers)
    #         for v_phone_number in v_phone_numbers:
    #             network.append({'type': 'edge',
    #                             'source': v_phone_number,
    #                             'target': 'speaker_{}'.format(v),
    #                             'properties': edge_properties
    #                         })
            
    #         for i, j in itertools.product(u_phone_numbers, v_phone_numbers):
    #             network.append({'type': 'edge',
    #                             'source': i,
    #                             'target': j,
    #                             'properties': edge_properties
    #                         })
            
    return network

# def _construct_network_aegis(nodes, edges):
#     network = []
#     for node in nodes:
#         network.append({'type': 'node',
#                         'id': nodes[node]['number'],
#                         'properties': {'type': 'phone_number',
#                                        'channels': nodes[node]}
#                        })
#     for u in edges:
#         for v in edges[u]:
#             edge_properties = dict()
#             edge_properties['type'] = 'conversations'
#             edge_properties['weight'] = edges[u][v]['weight']
#             if 'timestamps' in edges[u][v]:
#                 edge_properties['timestamps'] = edges[u][v]['timestamps']
#             network.append({'type': 'edge',
#                             'source': u,
#                             'target': v,
#                             'properties': edge_properties
#                            })
#     return network

def parse_wp5_output(wp5_outputs, threhold=50, calibration=False, directed=False):
    """
    build network from output of wp5
    :param wp5_outputs: dictionary converted from WP5's JSON object
    :param threhold:
    :param calibration:
    :param directed:
    :return:
    """

    # build channel-2-index map
    channels, channel2index = _generate_channels_and_index(wp5_outputs)
    # print(channels)

    # cluster
    labels = _cluster_from_voice_prints_matrix(channel2index, wp5_outputs, threhold, calibration)
    # print(labels)

    # generate nodes
    nodes = _generate_nodes(channels, channel2index, labels)
    # print("=================nodes==================")
    # print(nodes)

    # generate edges:
    edges = _generate_edges(channel2index, labels, wp5_outputs, directed)
    # print("=================edges==================")
    # print(edges)

    # construct network
    network = _construct_network(nodes, edges)
    # print("=================network==================")
    # print(network)

    return network


def parse_wp5_output_for_aegis(wp5_outputs, threhold=50, calibration=False, directed=False):
    """
    build network from output of wp5
    :param wp5_outputs: dictionary converted from WP5's JSON object
    :param directed:
    :return:
    """

    # build channel-2-index map
    channels, channel2index = _generate_channels_and_index(wp5_outputs)
    # print(channels)

    # cluster
    labels = _cluster_from_voice_prints_matrix(channel2index, wp5_outputs, threhold, calibration)
    print('labels:', labels)

    # generate nodes
    nodes = _generate_nodes_aegis(channels, channel2index, labels)
    print("=================nodes==================")
    print(nodes)

    # generate edges:
    # edges = _generate_edges(channel2index, labels, wp5_outputs, directed)
    edges = _generate_edges_aegis(channel2index, labels, wp5_outputs, directed)
    print("=================edges==================")
    print(edges)

    phone_number_edges = _generate_phone_number_edges_aegis(wp5_outputs, directed)
    print("=================phone_number_edges==================")
    print(phone_number_edges)

    # construct network
    network = _construct_network_aegis(nodes, edges, phone_number_edges, directed)
    # print("=================network==================")
    # print(network)

    return network


def dataset_from_wp5_output(network):
    """

    :param network: list of dictionary, each is a node or an edge
    :return:
    """
    dataset = BuiltinDataset(path_2_data=None, uploaded=False, from_file=False)
    dataset.nodes = {}
    dataset.edges = []
    dataset.adj_list = {}
    dataset.in_adj_list = {}
    dataset.node_types = {}
    dataset.edge_types = {}
    dataset.recent_changes = []
    for element in network:
        if element['type'] == 'node':
            node = element['properties']
            if 'community' in element:
                node['community'] = element['community']
                node['community_confidence'] = element['community_confidence']
            if 'social_influence_score' in element:
                node['social_influence_score'] = element['social_influence_score']
                node['normalized_social_influence'] = element['normalized_social_influence']
            dataset.nodes[element['id']] = node
            if 'type' in node:
                node_type = node['type']
                if node_type in dataset.node_types:
                    dataset.node_types[node_type] += 1
                else:
                    dataset.node_types[node_type] = 1

        elif element['type'] == 'edge':
            edge = {'source': element['source'], 'target': element['target'],
                    'observed': True, 'properties': element['properties']}
            if 'observed' in element:
                if element['observed'] == 'false':
                    edge['observed'] = 'false'
            dataset.edges.append(edge)
            e_index = len(dataset.edges) - 1
            source = edge['source']
            if source in dataset.adj_list:
                dataset.adj_list[source].append(e_index)
            else:
                dataset.adj_list[source] = [e_index]
            target = edge['target']
            if target in dataset.in_adj_list:
                dataset.in_adj_list[target].append(e_index)
            else:
                dataset.in_adj_list[target] = [e_index]

            if 'type' in element['properties']:
                edge_type = element['properties']['type']
                if edge_type in dataset.edge_types:
                    dataset.edge_types[edge_type] += 1
                else:
                    dataset.edge_types[edge_type] = 1
        else:
            continue
    return dataset
