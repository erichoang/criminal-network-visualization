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

 Test authorization middleware """
import pytest
from unittest import mock
from unittest.mock import patch, MagicMock
from ....conductor.src.middlewares.authorization import AuthorizationComponent
from ....conductor.src.helpers.auth_helpers import create_token
from ....conductor.src.auth_models import Role, User
from ....storage.builtin_datasets import BuiltinDataset


@pytest.fixture
def prepared_request():
    """ Prepare Request for middleware """
    request_mock = MagicMock()
    request_mock.auth = AuthorizationComponent.auth_header_prefix + create_token({"username": "admin"})
    return request_mock


def test_process_request_should_add_user_in_context(prepared_request):
    """ If Authorisation header is empty """
    with patch("sna.conductor.src.auth_graph.auth_dataset", BuiltinDataset("", from_file=False)) as dataset:
        auth_middleware = AuthorizationComponent()
        role = Role(dataset).add_role("User", 0)
        user = User(dataset).store_user("admin", "Pass1234", "User")
        auth_middleware.process_request(prepared_request, MagicMock())
        assert prepared_request.context.user.get_username() == "admin"
