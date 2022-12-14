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

 Test files collection action """
from unittest.mock import patch
from os.path import isfile
import pytest
from falcon.testing import TestClient
from requests_toolbelt import MultipartEncoder
from conductor.src.auth_models import User, Role
from conductor.src.helpers.auth_helpers import create_token


def test_files_should_return_list_of_files_on_get(client: TestClient, prepared_header, prepared_user: User):
    """ Files collection should return list of files in user's directory """
    user_folder = prepared_user.get_folder_path()
    file1 = "file1.json"
    file2 = "file2.json"
    with open(user_folder / file1, "w+") as file:
        file.write("example text")
    with open(user_folder / file2, "w+") as file:
        file.write("second example")
    response = client.simulate_get("/v1.0/files", headers=prepared_header)
    print(response.json)
    files_in_folder = response.json["files"]
    assert file1 in files_in_folder
    assert file2 in files_in_folder


def test_files_should_upload_file_on_post_request_with_multipart_type(client: TestClient, prepared_header, prepared_user, prepared_file):
    """ Files collection should upload file contents on post request with multipart request type on file field """
    filename = "testfile.json"
    multipart_file = MultipartEncoder(
        fields={
            "file": (filename, prepared_file, "application/json")
        }
    )
    prepared_header["Content-Type"] = multipart_file.content_type
    response = client.simulate_post("/v1.0/files", body=multipart_file.to_string(), headers=prepared_header)
    assert response.status_code == 201
    assert response.headers["Location"] == "/v1.0/files/" + filename
    assert isfile(prepared_user.get_folder_path() / filename)


def test_files_should_return_400_error_response_if_file_already_exists_on_post_request(client: TestClient, prepared_header, prepared_user, prepared_file):
    """ Files collection should return 400 response if file with given name already exists """
    filename = "testfile.json"
    multipart_file = MultipartEncoder(
        fields={
            "file": (filename, prepared_file, "application/json")
        }
    )
    with open(prepared_user.get_folder_path() / filename, "w+") as saved_file:
        saved_file.write(r"""{"id": "some other data!"}""")
    prepared_header["Content-Type"] = multipart_file.content_type
    response = client.simulate_post("/v1.0/files", body=multipart_file.to_string(), headers=prepared_header)
    assert response.status_code == 400
