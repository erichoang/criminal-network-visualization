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
# dataset from http://konect.uni-koblenz.de/networks/moreno_crime

import pickle
import sys
import os

# find path to root directory of the project so as to import from other packages
# to be refactored
# print('current script: storage/toy_datasets/imdb.py')
# print('os.path.abspath(__file__) = ', os.path.abspath(__file__))
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-3])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

from framework.interfaces import DataManager


def is_selected_type(selected_types, type):
    if selected_types is None:
        return True
    else:
        return type in selected_types


class MorenoCrimeDataset(DataManager):
    """

    """

    def __init__(self, connector, params):
        super(MorenoCrimeDataset, self).__init__(connector, params)
        self.dataset = pickle.load(open('%s/%s' % (path2root, params['data_file']), 'rb'))

    def get_network(self, network=None, node_ids=None, params=None):
        if node_ids is None:
            node_ids = ['person_%d' % i for i in range(self.dataset['num_persons'])]
            node_ids.extend(['crime_%d' % i for i in range(self.dataset['num_crimes'])])
        edges = []
        nodes = []
        involved_node_ids = set()
        for u in node_ids:
            if u.startswith('person_'):
                # the person
                m = int(u.split('_')[1])
                if m < 0 or m >= self.dataset['num_persons']:
                    continue
                if u not in involved_node_ids:
                    node = {'id': u,
                            'properties': {'type': 'person', 'name': self.dataset['name'][m],
                                           'gender': self.dataset['gender'][m]}}
                    nodes.append(node)
                # crimes
                for c in self.dataset['person_crimes'][m]:
                    roles = self.dataset['roles'][self.dataset['person_crimes'][m][c]]
                    for r in roles:
                        edge = {'source': u, 'target': 'crime_%d' % c, 'observed': True}
                        properties = {'weight': 1, 'type': r}
                        edge['properties'] = properties
                        edges.append(edge)

                    involved_node_id = 'crime_%d' % c
                    if involved_node_id not in involved_node_ids:
                        node = {'id': involved_node_id,
                                'properties': {'type': 'crime'}}
                        nodes.append(node)

            elif u.startswith('crime_'):
                # crime
                c = int(u.split('_')[1])
                if c < 0 or c >= self.dataset['num_crimes']:
                    continue
                if u not in involved_node_ids:
                    node = {'id': u, 'properties': {'type': 'crime'}}
                    nodes.append(node)
                # persons:
                for m in self.dataset['crime_persons'][c]:
                    roles = self.dataset['roles'][self.dataset['crime_persons'][c][m]]
                    for r in roles:
                        edge = {'source': u, 'target': 'person_%d' % m, 'observed': True}
                        properties = {'weight': 1, 'type': r}
                        edge['properties'] = properties
                        edges.append(edge)

                    involved_node_id = 'person_%d' % m
                    if involved_node_id not in involved_node_ids:
                        node = {'id': involved_node_id,
                                'properties': {'type': 'person', 'name': self.dataset['name'][m],
                                               'gender': self.dataset['gender'][m]}}
                        nodes.append(node)
            else:  # do nothing
                continue
        network = {'edges': edges, 'nodes': nodes}
        return network

    def get_neighbors(self, node_ids=None, network=None, params=None):
        founds = []
        not_founds = []
        for u in node_ids:
            if u.startswith('person_'):
                # the person
                m = int(u.split('_')[1])
                if m < 0 or m >= self.dataset['num_persons']:
                    not_founds.append(u)
                    continue
                neighbors = []
                for c in self.dataset['person_crimes'][m]:
                    neighbor = {'neighbor_id': 'crime_%d' % c, 'neighbor_name': '_NO_INFO_',
                                'type': 'crime'}
                    edges = []
                    roles = self.dataset['roles'][self.dataset['person_crimes'][m][c]]
                    for r in roles:
                        edges.append({'observed': True, 'weight': 1, 'type': r})
                    neighbor['edges'] = edges
                    neighbors.append(neighbor)
                    founds.append({'id': u, 'neighbors': neighbors})
            elif u.startswith('crime_'):
                # the person
                c = int(u.split('_')[1])
                if c < 0 or c >= self.dataset['num_crimes']:
                    not_founds.append(u)
                    continue
                neighbors = []
                for m in self.dataset['crime_persons'][c]:
                    neighbor = {'neighbor_id': 'person_%d' % m, 'neighbor_name': self.dataset['name'][m],
                                'type': 'person'}
                    edges = []
                    roles = self.dataset['roles'][self.dataset['crime_persons'][c][m]]
                    for r in roles:
                        edges.append({'observed': True, 'weight': 1, 'type': r})
                    neighbor['edges'] = edges
                    neighbors.append(neighbor)
                    founds.append({'id': u, 'neighbors': neighbors})
            else:
                not_founds.append(u)
        return {'found': founds, 'not_found': not_founds}

    def search_nodes(self, node_ids, network=None, params=None):
        founds = []
        not_founds = []
        for u in node_ids:
            if u.startswith('person_'):
                # the person
                m = int(u.split('_')[1])
                if m < 0 or m >= self.dataset['num_persons']:
                    not_founds.append(u)
                    continue
                node = {'id': u}
                properties = {}
                if params is not None:
                    for p in params:
                        if p == 'name':
                            properties[p] = self.dataset['name'][m]
                        elif p == 'gender':
                            properties[p] = self.dataset['gender'][m]
                        else:
                            properties[p] = '_NO_INFO_'
                else:
                    properties = {'name': self.dataset['name'][m], 'gender': self.dataset['gender'][m]}
                node['properties'] = properties
                founds.append(node)
            elif u.startswith('crime_'):
                # the person
                c = int(u.split('_')[1])
                if c < 0 or c >= self.dataset['num_crimes']:
                    not_founds.append(u)
                    continue
                node = {'id': u}
                properties = {}
                if params is not None:
                    for p in params:
                        properties[p] = '_NO_INFO_'
                node['properties'] = properties
                founds.append(node)
            else:
                not_founds.append(u)
        return {'found': founds, 'not_found': not_founds}
