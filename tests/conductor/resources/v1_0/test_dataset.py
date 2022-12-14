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

 Unit tests for dataset resource """
import pytest
from os.path import isfile
from unittest.mock import patch
from falcon.testing import TestClient
from conductor.src.auth_models import User
from conductor.src.helpers.network_helpers import split_to_network


@pytest.fixture
def prepared_dataset(prepared_user: User):
    """ Create dataset to do queries on """
    prepared_user.create_dataset("data", "stuff", None, from_file=False)
    dataset = prepared_user.get_dataset("data")
    dataset.save_nodes({
        "Satam_Suqami": {"type": "person", "name": "Satam Suqami", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False},
        "Majed_Moqed": {"type": "person", "name": "Majed Moqed", "flight": "AA #77 Pentagon", "attend_Las_Vegas_Meeting": False},
        "Khalid_Al-Mihdhar": {"type": "person", "name": "Khalid Al-Mihdhar", "flight": "AA #77 Pentagon", "attend_Las_Vegas_Meeting": False},
        "Nawaf_Alhazmi": {"type": "person", "name": "Nawaf Alhazmi", "flight": "AA #77 Pentagon", "attend_Las_Vegas_Meeting": True}
    })
    dataset.save_edges([
        {"source": "Majed_Moqed", "target": "Khalid_Al-Mihdhar", "properties": {"type": "prior_contact", "observed": True, "weight": 1}},
        {"source": "Majed_Moqed", "target": "Nawaf_Alhazmi", "properties": {"type": "prior_contact", "observed": True, "weight": 1}}
    ])
    return dataset


def test_dataset_resource_should_return_network_by_node_ids_on_post_request(client: TestClient, prepared_header, prepared_dataset, prepared_user: User):
    """ post request with node ids on dataset resource should return its network """
    payload = {
        "nodes": [
            "Majed_Moqed",
            "Nawaf_Alhazmi"
        ],
        "params": {}
    }
    response = client.simulate_post("/v1.0/datasets/data", headers=prepared_header, json=payload)
    network_comparison = prepared_dataset.get_network(payload["nodes"], payload["params"])
    print(response.json)
    assert response.json["network"] == split_to_network(network_comparison["nodes"], network_comparison["edges"])


def test_dataset_resource_should_save_network_on_patch_request(client: TestClient, prepared_header, prepared_dataset, prepared_user: User):
    """ patch request on dataset resource should save or update all network items """
    payload = {
        "network": [
            {"type": "node", "id": "Satam_Suqami", "properties": {"type": "person", "name": "Satam Suqami", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": True}},
            {"type": "edge", "source": "Majed_Moqed", "target": "Khalid_Al-Mihdhar", "properties": {"type": "prior_contact", "observed": False, "weight": 0.5}}
        ]
    }
    response = client.simulate_patch("/v1.0/datasets/data", headers=prepared_header, json=payload)
    print(response.json)
    assert prepared_dataset.nodes["Satam_Suqami"]["attend_Las_Vegas_Meeting"] == True
    edge = next(e for e in prepared_dataset.edges if e["source"] == "Majed_Moqed" and e["target"] == "Khalid_Al-Mihdhar")
    assert edge["properties"]["observed"] == False
    assert edge["properties"]["weight"] == 0.5


@pytest.mark.skip
def test_dataset_resource_should_delete_nodes_and_edges_by_provided_ids(client: TestClient, prepared_header, prepared_dataset, prepared_user: User):
    """ delete request on dataset resource should remove edges and nodes from dataset """
    payload = {
        "edges": [
            {"source": "Majed_Moqed", "target": "Nawaf_Alhazmi"}
        ],
        "nodes": [
            "Satam_Suqami"
        ]
    }
    response = client.simulate_delete("/v1.0/datasets/data", headers=prepared_header, json=payload)
    print(prepared_dataset.edges)
    with pytest.raises(KeyError):
        prepared_dataset.nodes["Satam_Suqami"]
    with pytest.raises(StopIteration):
        next(e for e in prepared_dataset.edges if e["source"] == "Majed_Moqed" and e["target"] == "Nawaf_Alhazmi")
