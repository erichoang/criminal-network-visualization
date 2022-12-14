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


class ImdbDataset(DataManager):
    """

    """

    def __init__(self, connector, params):
        super(ImdbDataset, self).__init__(connector, params)
        self.dataset = pickle.load(open('%s/%s' % (path2root, params['data_file']), 'rb'))

    def get_network(self, network_id=None, node_ids=None, params=None):
        if node_ids is None:
            node_ids = ['movie_%d' % i for i in range(len(self.dataset['movies']))]
            node_ids.extend(['actor_%d' % i for i in range(len(self.dataset['actors']))])
            node_ids.extend(['director_%d' % i for i in range(len(self.dataset['directors']))])
        edges = []
        nodes = []
        involved_node_ids = set()
        for u in node_ids:
            if u.startswith('movie_'):
                # the movie
                m = int(u.split('_')[1])
                if u not in involved_node_ids:
                    node = {'id': u,
                            'properties': {'type': 'movie', 'name': self.dataset['movies'][m]}}
                    nodes.append(node)
                # actors
                for a in self.dataset['movie_actors'][m]:
                    edge = {'source': u, 'target': 'actor_%d' % a, 'observed': True}
                    properties = {'weight': 1, 'type': 'features'}
                    edge['properties'] = properties
                    edges.append(edge)

                    involved_node_id = 'actor_%d' % a
                    if involved_node_id not in involved_node_ids:
                        node = {'id': involved_node_id,
                                'properties': {'type': 'actor', 'name': self.dataset['actors'][a]}}
                        nodes.append(node)
                # directors
                for d in self.dataset['movie_directors'][m]:
                    edge = {'source': u, 'target': 'director_%d' % d, 'observed': True}
                    properties = {'weight': 1, 'type': 'directed_by'}
                    edge['properties'] = properties
                    edges.append(edge)

                    involved_node_id = 'director_%d' % d
                    if involved_node_id not in involved_node_ids:
                        node = {'id': involved_node_id,
                                'properties': {'type': 'director', 'name': self.dataset['directors'][d]}}
                        nodes.append(node)
            elif u.startswith('actor_'):
                # actor
                if u not in involved_node_ids:
                    a = int(u.split('_')[1])
                    node = {'id': u,
                            'properties': {'type': 'actor', 'name': self.dataset['actors'][a]}}
                    nodes.append(node)
                # movies:
                for m in self.dataset['actor_movies'][a]:
                    edge = {'source': u, 'target': 'movie_%d' % m, 'observed': True}
                    properties = {'weight': 1, 'type': 'plays_in'}
                    edge['properties'] = properties
                    edges.append(edge)

                    involved_node_id = 'movie_%d' % m
                    if involved_node_id not in involved_node_ids:
                        node = {'id': involved_node_id,
                                'properties': {'type': 'movie', 'name': self.dataset['movies'][m]}}
                        nodes.append(node)
            elif u.startswith('director_'):
                # director
                if u not in involved_node_ids:
                    d = int(u.split('_')[1])
                    node = {'id': u,
                            'properties': {'type': 'director', 'name': self.dataset['directors'][d]}}
                    nodes.append(node)
                # movies:
                for m in self.dataset['director_movies'][d]:
                    edge = {'source': u, 'target': 'movie_%d' % m, 'observed': True}
                    properties = {'weight': 1, 'type': 'directs'}
                    edge['properties'] = properties
                    edges.append(edge)

                    involved_node_id = 'movie_%d' % m
                    if involved_node_id not in involved_node_ids:
                        node = {'id': involved_node_id,
                                'properties': {'type': 'movie', 'name': self.dataset['movies'][m]}}
                        nodes.append(node)
            else:  # do nothing
                continue
        network = {'edges': edges, 'nodes': nodes}
        return network
