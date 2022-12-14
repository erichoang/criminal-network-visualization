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
import json

# find path to root directory of the project so as to import from other packages
# print('current script: visualizer/test_imdb_toy_dataset.py')
# print('os.path.abspath(__file__) = ', os.path.abspath(__file__))
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

from storage.toy_datasets.toy_data_manager import ToyDataManager
from analyzer.request_taker import InMemoryAnalyzer
from storage.builtin_datasets import BuiltinDatasetsManager


def test_community_detection():
    data_manager = ToyDataManager(connector=None, params=None)
    network_id = 'moreno_crime'
    network = data_manager.get_network(network=network_id)

    test_network = {"edges": network.get('edges')[:100],
                    "nodes": network.get('nodes')[:100]}

    
    connector = None  # no connection needed for this file-base datasets
    params = None  # no parameter defined for now
    data_manager = BuiltinDatasetsManager(connector, params)

    # define task for testing
    task_id = "community_detection"
    task_options = {
        "method": "modularity",
        # "method": "k_cliques",
        # "method": "spectral",
        # "method": "asyn_lpa",
        # "method": "label_propagation",
        # "method": "bipartition",
        # "method": "hierarchical",
        # 'parameters': {}
        "parameters": {'K': 2}
    }

    task = {"task_id": task_id,
            "network": test_network,
            "options": task_options}

    # call analyzer
    analyzer = InMemoryAnalyzer()
    result = analyzer.perform_analysis(task=task, params=None)
    print(result)

    network_analysis_output_dir = os.path.join(path2root, 'analysis_results') 
    if not os.path.exists(network_analysis_output_dir):
        os.makedirs(network_analysis_output_dir)

    filename_result = '%s_%s_%s.json' % (task_id, task_options['method'], network_id)
    filepath_result = os.path.join(network_analysis_output_dir, filename_result)

    # for key in result.keys():
    #     if type(key) is not str:
    #         try:
    #             result[str(key)] = result[key]
    #         except:
    #             try:
    #                 result[repr(key)] = result[key]
    #             except:
    #                 pass
    #         del result[key]

    with open(filepath_result, 'w') as outfile:
        json.dump(result, outfile, indent=4)
    print('Dumped successfuly:', filepath_result)


# print("communities = ", result[0][0])
# print("membership = ", result[0][1])

if __name__ == '__main__':
    test_community_detection()
