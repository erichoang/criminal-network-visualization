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

# find path to root directory of the project so as to import from other packages
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

from framework.interfaces import AnalysisRequester
from analyzer.community_detection import CommunityDetector
from analyzer.social_influence_analysis import SocialInfluenceAnalyzer
from analyzer.link_prediction import LinkPredictor
from analyzer.node_embedding import NodeEmbedder

from analyzer import community_detection
from analyzer import link_prediction
from analyzer import social_influence_analysis
from analyzer import node_embedding


def get_info():
    """
    get information about available methods for each analysis task
    :return: dictionary: keys are tasks' id, values are dictionaries that describe the methods available for the task
                each in the following format:
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
    info = {'community_detection': community_detection.get_info(),
            'link_prediction': link_prediction.get_info(),
            'social_influence_analysis': social_influence_analysis.get_info(),
            'node_embedding': node_embedding.get_info()
            }
    return info


class InMemoryAnalyzer(AnalysisRequester):
    def __init__(self):
        """
        #TODO: more to be added
        """
        self.community_detector = None
        self.social_influence_analyzer = None
        self.link_predictor = None
        self.node_embedder = None

    def perform_analysis(self, task, params):
        """
        request to perform an analysis task
        :param task: dictionary that contains information about a requested task, in the following format
            {
                "task_id": id of the task, either
                        "community_detection",
                        "social_influence_analysis"
                        "link_prediction",
                        "node_embedding"
                        # TODO: more to be added
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
        network = task['network']
        if type(network) == str:
            # TODO: retrieve network from database
            print('in-database network is not supported')
            # TODO: what should be returned?
            return None
        algorithm = task['options']['method']
        algorithm_params = task['options']['parameters']
        # print('algorithm_params = ', algorithm_params)

        # print('task = ', task['task_id'])
        if task['task_id'] == 'community_detection':
            # print('task: community detection\n\tmethod = ', algorithm)
            # print('\tparams = ', cd_params)
            self.community_detector = CommunityDetector(algorithm)
            return self.community_detector.perform(network, algorithm_params)
        elif task['task_id'] == 'social_influence_analysis':
            self.social_influence_analyzer = SocialInfluenceAnalyzer(algorithm)
            return self.social_influence_analyzer.perform(network, algorithm_params)
        elif task['task_id'] == 'link_prediction':
            self.link_predictor = LinkPredictor(algorithm)
            return self.link_predictor.perform(network, algorithm_params)
        elif task['task_id'] == 'node_embedding':
            self.node_embedder = NodeEmbedder(algorithm)
            return self.node_embedder.perform(network, algorithm_params)
        else:
            # TODO: what should be return?
            print('task %s is not defined' % task['task_id'])
            return None
