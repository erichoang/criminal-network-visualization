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


class EnronDataset(DataManager):
    """

    """

    def __init__(self, connector, params):
        super(EnronDataset, self).__init__(connector, params)
        # print('in enron data manager')
        # print('pwd = ', os.getcwd())
        self.dataset = pickle.load(open('%s/%s' % (path2root, params['data_file']), 'rb'))

    def get_network(self, network=None, node_ids=None, params=None):
        if node_ids is None:
            node_ids = [u for u in self.dataset['nodes']]
        edges = []
        nodes = []

        selected_types = None
        if params is not None:
            if 'types' in params:
                selected_types = set(params['types'])

        involved_node_ids = set()
        for u in node_ids:
            if u in self.dataset['edges']:
                if not is_selected_type(selected_types, self.dataset['nodes'][u]['type']):
                    continue

                if u not in involved_node_ids:
                    nodes.append({'id': u, 'properties': self.dataset['nodes'][u]})

                for v in self.dataset['edges'][u]:
                    if not is_selected_type(selected_types, self.dataset['nodes'][v]['type']):
                        continue
                    edge = {'source': u, 'target': v, 'observed': True}
                    properties = {'weight': self.dataset['edges'][u][v], 'type': 'send_mails'}
                    edge['properties'] = properties
                    edges.append(edge)

                    if v not in involved_node_ids:
                        nodes.append({'id': v, 'properties': self.dataset['nodes'][u]})
            else:  # do nothing
                continue
        network = {'edges': edges, 'nodes': nodes}
        return network

    def get_neighbors(self, node_ids, network=None, params=None):
        founds = []
        not_founds = []
        for u in node_ids:
            if u in self.dataset['edges']:
                neighbors = []
                for v in self.dataset['edges'][u]:
                    neighbor = {'neighbor_id': v, 'neighbor_name': self.dataset['nodes'][v]['name'],
                                'type': self.dataset['nodes'][v]['type']}
                    edges = [{'observed': True, 'weight': self.dataset['edges'][u][v], 'type': 'send_mails'}]
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
            if u in self.dataset['nodes']:
                node = {'id': u}
                properties = {}
                if params is not None:
                    for p in params:
                        if p in self.dataset['nodes'][u]:
                            properties[p] = self.dataset['nodes'][u][p]
                        else:
                            properties[p] = '_NO_INFO_'
                else:
                    for p in self.dataset['nodes'][u]:
                        properties[p] = self.dataset['nodes'][u][p]
                node['properties'] = properties
                founds.append(node)
            else:
                not_founds.append(u)
        return {'found': founds, 'not_found': not_founds}
