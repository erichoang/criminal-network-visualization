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
import json
import seaborn as sns


class Style:
    """
    Represents and works with the style of the (cytoscape) visualization
    """
    def __init__(self, file):
        """
        Initialize the style object using a stylesheet
        :param file: A json object defining a cytoscape style (see visualizer/cyto_style.json)
        """
        self.file = file
        self.stylesheet = _load_from_file(file)
        self.selected_nodes = [] # [list of: {node: node_id, neighbors: list of neighbor ids}]
        self.selected_neighbors = {}
        # Valid names of shaped which can be used to style nodes in cytoscape
        self.shapes = ['ellipse', 'triangle', 'rectangle', 'pentagon',
                       'hexagon', 'octagon', 'star', 'heptagon', 'rhomboid']
        self.types = []

    def set_type_styles(self, types):
        """
        Set a each type of nodes to a different variant of blue.
        :param types: List of node types.
        """
        new_types = list(set(types) - set(self.types))
        offset = len(self.types)
        colors = sns.color_palette('Set2', n_colors=len(types)).as_hex()
        for i, t in enumerate(new_types):
            self.types.append(new_types[i])
            style = {
                'selector': "node[type = '" + str(new_types[i]) +
                            "'][visualisation_social_influence_score < 0][community < 0][!highlighted]",
                'style': {'background-color': str(colors[i + offset])}}
            self.stylesheet.append(style)
            style = {
                'selector': "node[type = '" + str(new_types[i]) +
                            "']",
                'style': {'shape': str(self.shapes[i + offset])}}
            self.stylesheet.append(style)

    def reset(self):
        """
        Reload the default stylesheet.
        """
        self.stylesheet = _load_from_file(self.file)
        self.selected_nodes = []
        self.selected_neighbors = {}
        self.types = []

    def set_edge_prob(self, probability):
        for idx, style in reversed(list(enumerate(self.stylesheet))):
            if style['selector'].startswith('edge[prob'):
                del self.stylesheet[idx]
                break
        value = "edge[probability<" + str(probability) + "]"
        style = {
            'selector': value,
            'style': {'display': 'none'}
        }
        self.stylesheet.append(style)



def _load_from_file(file):
    with open(file) as file:
        return json.load(file)
