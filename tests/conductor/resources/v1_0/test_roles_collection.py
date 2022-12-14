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

 Tests for roles collection resource """
from unittest.mock import patch
import pytest
from falcon import HTTP_201
from falcon.testing import TestClient
from storage.builtin_datasets import BuiltinDataset
from conductor.src.auth_models import Role


@pytest.fixture
def prepared_auth_dataset():
    """ patch dataset for authentication """
    with patch("conductor.src.resources.roles_collection.auth_dataset", BuiltinDataset("", from_file=False)) as mock_dataset:
        Role(mock_dataset).add_role("User", 0)
        Role(mock_dataset).add_role("Admin", 1)
        yield mock_dataset


def test_roles_collection_should_return_all_roles_on_get_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ request on roles collection resource should return list of all the resources """
    response = client.simulate_get("/v1.0/roles", headers=auth_headers)
    decoded_payload = response.json
    expected_payload = [
        {"name": r.get_name(), "rank": r.get_rank()}
        for r in Role.get_all(prepared_auth_dataset)
    ]
    assert all([ex == de for ex, de in zip(expected_payload, decoded_payload["roles"])])


def test_roles_collection_should_add_role_on_post(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on roles collection should add new role into authentification graph """
    payload = {
        "name": "Onlooker",
        "rank": 2
    }
    response = client.simulate_post("/v1.0/roles", json=payload, headers=auth_headers)
    assert Role(prepared_auth_dataset).get_role_vertex(payload["name"])


def test_roles_collection_should_return_new_role_location(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on roles resource collection should add Location header with link to role and return 201 response """
    payload = {
        "name": "Onlooker",
        "rank": 2
    }
    response = client.simulate_post("/v1.0/roles", json=payload, headers=auth_headers)
    assert response.status == HTTP_201
    assert response.headers["Location"] == "/v1.0/roles/" + payload["name"]
