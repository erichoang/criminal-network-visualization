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
import pytest
from conductor.src.helpers.network_helpers import network_to_split, split_to_network


def test_network_to_split_should_return_nodes_and_edges_dictionaries():
    """ network_to_split should return dictionary with nodes and edges keys """
    example_network = [
        {"type": "node", "id": "Satam_Suqami", "properties": {"type": "person", "name": "Satam Suqami", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}},
        {"type": "node", "id": "Wail_Alshehri", "properties": {"type": "person", "name": "Wail Alshehri", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}},
        {"type": "edge", "source": "Majed_Moqed", "target": "Khalid_Al-Mihdhar", "properties": {"type": "prior_contact", "observed": True, "weight": 1}},
        {"type": "edge", "source": "Majed_Moqed", "target": "Nawaf_Alhazmi", "properties": {"type": "prior_contact", "observed": True, "weight": 1}}
    ]
    result = network_to_split(example_network)
    assert example_network[0] in result["nodes"] and example_network[1] in result["nodes"]
    assert example_network[2] in result["edges"] and example_network[3] in result["edges"]

def test_split_to_network_should_return_list_of_nodes_and_edges_combined():
    """ split_to_network should combine edges and nodes """
    example_split = {
        "edges": [
            {"source": "Majed_Moqed", "target": "Khalid_Al-Mihdhar", "properties": {"type": "prior_contact", "observed": True, "weight": 1}},
            {"source": "Majed_Moqed", "target": "Nawaf_Alhazmi", "properties": {"type": "prior_contact", "observed": True, "weight": 1}}
        ],
        "nodes": [
            {"id": "Satam_Suqami", "properties": {"type": "person", "name": "Satam Suqami", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}},
            {"id": "Wail_Alshehri", "properties": {"type": "person", "name": "Wail Alshehri", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}}
        ]
    }
    result = split_to_network(example_split["nodes"], example_split["edges"])
    assert all(el in result for el in example_split["edges"] + example_split["nodes"])
