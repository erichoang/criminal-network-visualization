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

 Tests for user collection resource """
from unittest.mock import patch
import pytest
from falcon import HTTP_201
from falcon.testing import TestClient
from conductor.src.hooks.secure_resource import NotAuthorizedError, NotEnoughPrivileges
from conductor.src.helpers.auth_helpers import create_token
from conductor.src.auth_models import User, Role
from storage.builtin_datasets import BuiltinDataset


@pytest.fixture
def prepared_auth_dataset():
    """ patch dataset for authentication """
    with patch("conductor.src.resources.users_collection.auth_dataset", BuiltinDataset("", from_file=False)) as mock_dataset:
        Role(mock_dataset).add_role("User", 0)
        Role(mock_dataset).add_role("Admin", 1)
        l3s_user = User(mock_dataset).store_user("l3s", "Superpassword1111", "User")
        admin_user = User(mock_dataset).store_user("admin", "Pass1234", "Admin")
        yield mock_dataset
        l3s_user.delete()
        admin_user.delete()


def test_users_collection_get_should_return_list_of_all_users(client: TestClient, auth_headers, prepared_auth_dataset):
    """ get request on users collection resource should list all users """
    response = client.simulate_get("/v1.0/users", headers=auth_headers)
    decoded_payload = response.json
    expected_payload = [
        {"username": u.get_username(), "role": u.role.get_name()}
        for u in User.get_all(prepared_auth_dataset)
    ]
    assert all([ex == de for ex, de in zip(expected_payload, decoded_payload["users"])])


def test_users_collection_post_should_add_new_user_in_auth_graph(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on users collection resource should add new user """
    payload = {
        "username": "billy",
        "password": "Superpass9999",
        "role": "User"
    }
    response = client.simulate_post("/v1.0/users", json=payload, headers=auth_headers)
    assert User(prepared_auth_dataset).authenticate(payload["username"], payload["password"])


def test_users_collection_post_should_return_201_response_with_Location_header(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on users resource collection should add Location header with link to user and return 201 response """
    payload = {
        "username": "billy",
        "password": "Superpass9999",
        "role": "User"
    }
    response = client.simulate_post("/v1.0/users", json=payload, headers=auth_headers)
    assert response.status == HTTP_201
    assert response.headers["Location"] == "/v1.0/users/" + payload["username"]
