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

 Unit tests for file resource """
import pytest
from os.path import isfile
from unittest.mock import patch
from falcon.testing import TestClient
from requests_toolbelt import MultipartEncoder
from conductor.src.auth_models import User, Role
from .conftest import EXAMPLE_NETWORK


def test_file_should_return_file_contents_on_get(client: TestClient, prepared_header, prepared_user: User):
    """ get request on file resource should return file contents """
    filename = "file1.json"
    file_contents = "example text"
    with open(prepared_user.get_folder_path() / filename, "w+") as file:
        file.write(file_contents)
    response = client.simulate_get("/v1.0/files/" + filename, headers=prepared_header)
    assert response.text == file_contents


def test_file_resource_should_upload_file_by_filename_on_post(client: TestClient, prepared_header, prepared_file, prepared_user: User):
    """ post request on file resource should upload new file """
    filename = "testfile.json"
    multipart_file = MultipartEncoder(
        fields={
            "file": (filename, prepared_file, "application/json")
        }
    )
    prepared_header["Content-Type"] = multipart_file.content_type
    response = client.simulate_post("/v1.0/files/" + filename, body=multipart_file.to_string(), headers=prepared_header)
    with open(prepared_user.get_folder_path() / filename, "r+") as saved_file:
        assert "".join(saved_file.readlines()) == EXAMPLE_NETWORK
        assert response.headers["Location"] == "/v1.0/files/" + filename
        assert response.status_code == 201


def test_file_resource_should_remove_file_on_delete_request(client: TestClient, prepared_header, prepared_user: User):
    """ delete request on file resource should remove the file from user folder """
    filename = "testfile.json"
    with open(prepared_user.get_folder_path() / filename, "w+") as saved_file:
        saved_file.write(r"""{"id": "some other data!"}""")
    response = client.simulate_delete("/v1.0/files/" + filename, headers=prepared_header)
    print(response.text)
    assert response.status_code == 200
    assert not isfile(prepared_user.get_folder_path() / filename)


def test_file_resource_should_upload_file_by_filename_if_file_does_not_exist_on_put(client: TestClient, prepared_header, prepared_file, prepared_user: User):
    """ put request on file resource should add new file if it doesn't exists """
    filename = "testfile.json"
    multipart_file = MultipartEncoder(
        fields={
            "file": (filename, prepared_file, "application/json")
        }
    )
    prepared_header["Content-Type"] = multipart_file.content_type
    with open(prepared_user.get_folder_path() / filename, "w+") as saved_file:
        saved_file.write(r"""{"id": "some other data!"}""")
    response = client.simulate_put("/v1.0/files/" + filename, body=multipart_file.to_string(), headers=prepared_header)
    with open(prepared_user.get_folder_path() / filename, "r+") as saved_file:
        assert "".join(saved_file.readlines()) == EXAMPLE_NETWORK
        assert response.status_code == 200


def test_file_resource_should_replace_file_by_filename_if_file_exists_on_put(client: TestClient, prepared_header, prepared_file, prepared_user: User):
    """  """
    """ put request on file resource should add new file if it doesn't exists """
    filename = "testfile.json"
    multipart_file = MultipartEncoder(
        fields={
            "file": (filename, prepared_file, "application/json")
        }
    )
    prepared_header["Content-Type"] = multipart_file.content_type
    response = client.simulate_put("/v1.0/files/" + filename, body=multipart_file.to_string(), headers=prepared_header)
    with open(prepared_user.get_folder_path() / filename, "r+") as saved_file:
        assert "".join(saved_file.readlines()) == EXAMPLE_NETWORK
        assert response.headers["Location"] == "/v1.0/files/" + filename
        assert response.status_code == 201
