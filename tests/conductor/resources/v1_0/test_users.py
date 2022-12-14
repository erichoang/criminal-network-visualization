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

 Tests for user resource """
from unittest.mock import patch
import pytest
from falcon import HTTP_201, HTTP_200
from falcon.testing import TestClient
from conductor.src.hooks.secure_resource import NotAuthorizedError, NotEnoughPrivileges
from conductor.src.helpers.auth_helpers import create_token
from conductor.src.auth_models import User, Role, AuthRecordNotFoundError
from storage.builtin_datasets import BuiltinDataset


@pytest.fixture
def prepared_auth_dataset():
    """ patch dataset for authentication """
    with patch("conductor.src.resources.users.auth_dataset", BuiltinDataset("", from_file=False)) as mock_dataset:
        Role(mock_dataset).add_role("User", 0)
        Role(mock_dataset).add_role("Admin", 1)
        user = User(mock_dataset).store_user("admin", "Pass1234", "Admin")
        yield mock_dataset


def test_users_should_return_user_role_on_get_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ post request on users resource should return user role in response body """
    username = "admin"
    response = client.simulate_get("/v1.0/users/" + username, headers=auth_headers)
    expected_user = User(prepared_auth_dataset).identify(username).get_role()
    assert response.json["role"]["name"] == expected_user.get_name()


def test_users_should_create_user_on_put_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ put request on users should create user if not found in authentification graph """
    username = "user"
    payload = {
        "password": "Pass1234",
        "role": "User"
    }
    response = client.simulate_put("/v1.0/users/" + username, headers=auth_headers, json=payload)
    assert User(prepared_auth_dataset).authenticate(username, payload["password"])


def test_users_should_return_location_header_if_user_created_on_put_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ put request on users should return Location header with path to user and 201 code """
    username = "user"
    payload = {
        "password": "Pass1234",
        "role": "User"
    }
    response = client.simulate_put("/v1.0/users/" + username, headers=auth_headers, json=payload)
    assert response.status == HTTP_201
    assert response.headers["Location"] == "/v1.0/users/" + username


@pytest.mark.skip
def test_users_should_replace_user_on_put_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ put request on users should replace existing user if found """
    username = "admin"
    payload = {
        "password": "Superpass333",
        "role": "User"
    }
    response = client.simulate_put("/v1.0/users/" + username, headers=auth_headers, json=payload)
    print(prepared_auth_dataset.nodes)
    print(prepared_auth_dataset.edges)
    user = User(prepared_auth_dataset).authenticate(username, payload["password"])
    assert response.status == HTTP_200
    assert payload["role"] == user.get_role().get_name()


def test_users_should_create_user_on_patch_if_not_found(client: TestClient, auth_headers, prepared_auth_dataset):
    """ patch request on users resource should create new user if not found by username """
    username = "user"
    payload = {
        "password": "Pass1234",
        "role": "User"
    }
    response = client.simulate_patch("/v1.0/users/" + username, headers=auth_headers, json=payload)
    assert User(prepared_auth_dataset).authenticate(username, payload["password"])


def test_users_should_return_location_header_if_user_created_on_patch_request(client: TestClient, auth_headers, prepared_auth_dataset):
    """ patch request on users should return Location header with path to user and 201 code """
    username = "user"
    payload = {
        "password": "Pass1234",
        "role": "User"
    }
    response = client.simulate_patch("/v1.0/users/" + username, headers=auth_headers, json=payload)
    assert response.status == HTTP_201
    assert response.headers["Location"] == "/v1.0/users/" + username


def test_users_should_modify_user_password_on_patch_request_if_password_given(client: TestClient, auth_headers, prepared_auth_dataset):
    """ patch request on users should modify user password if given in request body"""
    username = "admin"
    payload = {
        "password": "SuperDuperPass3"
    }
    response = client.simulate_patch("/v1.0/users/" + username, headers=auth_headers, json=payload)
    assert response.status == HTTP_200
    assert User(prepared_auth_dataset).authenticate(username, payload["password"])


def test_users_should_modify_user_role_on_patch_request_if_role_given(client: TestClient, auth_headers, prepared_auth_dataset):
    """ patch request on users should change user role by name """
    username = "admin"
    payload = {
        "role": "User"
    }
    response = client.simulate_patch("/v1.0/users/" + username, headers=auth_headers, json=payload)
    user = User(prepared_auth_dataset).identify(username)
    assert response.status == HTTP_200
    assert payload["role"] == user.get_role().get_name()


def test_users_should_remove_user_if_delete_request_issued(client: TestClient, auth_headers, prepared_auth_dataset):
    """ delete request on users should remove user from storage by username """
    username = "admin"
    response = client.simulate_delete("/v1.0/users/" + username, headers=auth_headers)
    assert response.status == HTTP_200
    with pytest.raises(AuthRecordNotFoundError):
        User(prepared_auth_dataset).identify(username)
