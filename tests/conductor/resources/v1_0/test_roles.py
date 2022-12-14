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

 Unit tests for role resource """
import pytest
from unittest.mock import patch
from falcon.testing import TestClient
from requests_toolbelt import MultipartEncoder
from storage.builtin_datasets import BuiltinDataset
from conductor.src.auth_models import User, Role, AuthRecordNotFoundError


@pytest.fixture
def prepared_auth_dataset():
    """ patch dataset for authentication """
    with patch("conductor.src.resources.roles.auth_dataset", BuiltinDataset("", from_file=False)) as mock_dataset:
        Role(mock_dataset).add_role("User", 0)
        Role(mock_dataset).add_role("Admin", 1)
        admin_user = User(mock_dataset).store_user("admin", "Pass1234", "Admin")
        yield mock_dataset
        admin_user.delete()


def test_role_resource_should_return_role_rank_on_get_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ get request on role resource should return name and rank of the role """
    role_name = "Admin"
    response = client.simulate_get("/v1.0/roles/" + role_name, headers=auth_headers)
    payload = response.json
    expected_role = Role(prepared_auth_dataset).get_role_vertex(role_name)
    assert payload["name"] == expected_role.get_name()
    assert payload["rank"] == expected_role.get_rank()


def test_role_resource_should_create_new_role_on_post_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on role resource should create new role """
    role_name = "Onlooker"
    payload = {
        "rank": 2
    }
    response = client.simulate_post("/v1.0/roles/" + role_name, headers=auth_headers, json=payload)
    created_role = Role(prepared_auth_dataset).get_role_vertex(role_name)
    assert response.status_code == 201
    assert payload["rank"] == created_role.get_rank()


def test_role_resource_should_return_AlreadyExistsError_if_role_exists_on_post_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on role resource should return AlreadyExistsError with 400 response code if role already exists """
    role_name = "Admin"
    payload = {
        "rank": 1
    }
    response = client.simulate_post("/v1.0/roles/" + role_name, headers=auth_headers, json=payload)
    assert response.status_code == 400


def test_role_resource_should_update_role_parameters_on_patch_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ patch request should update role name or rank on patch request """
    role_name = "Admin"
    payload = {
        "rank": 2
    }
    response = client.simulate_patch("/v1.0/roles/" + role_name, headers=auth_headers, json=payload)
    created_role = Role(prepared_auth_dataset).get_role_vertex(role_name)
    assert created_role.get_rank() == payload["rank"]
    assert response.status_code == 200


def test_role_resource_should_create_role_if_role_does_not_exist_on_patch_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ patch request should create new role if role not found """
    role_name = "Onlooker"
    payload = {
        "rank": 2
    }
    response = client.simulate_patch("/v1.0/roles/" + role_name, headers=auth_headers, json=payload)
    created_role = Role(prepared_auth_dataset).get_role_vertex(role_name)
    assert created_role.get_rank() == payload["rank"]
    assert response.status_code == 201
