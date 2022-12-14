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
# print('current script: storage/toy_datasets/toy_data_manager.py')
# print('os.path.abspath(__file__) = ', os.path.abspath(__file__))
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-3])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

from framework.interfaces import DataManager
from storage.toy_datasets.enron import EnronDataset
from storage.toy_datasets.moreno_crime import MorenoCrimeDataset


class ToyDataManager(DataManager):
    """

    """

    def __init__(self, connector, params):
        super(ToyDataManager, self).__init__(connector, params)
        self.datasets = {'enron': EnronDataset(connector, {'data_file': 'datasets/enron_dataset.pkl'}),
                         'moreno_crime': MorenoCrimeDataset(connector,
                                                            params={'data_file': 'datasets/moreno_crime_dataset.pkl'})}

    def get_network(self, network, node_ids=None, params=None):
        if network in self.datasets:
            return self.datasets[network].get_network(node_ids=node_ids, params=params)
        else:
            return {'edges': [], 'nodes': []}

    def get_neighbors(self, node_ids, network, params=None):
        if network in self.datasets:
            return self.datasets[network].get_neighbors(node_ids=node_ids, params=params)
        else:
            return {'found': [], 'not_found': node_ids}

    def search_nodes(self, node_ids, network, params=None):
        if network in self.datasets:
            return self.datasets[network].search_nodes(node_ids=node_ids, params=params)
        else:
            return {'found': [], 'not_found': node_ids}
