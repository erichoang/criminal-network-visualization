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

 Tests for Secure hook """
from unittest.mock import MagicMock
import pytest
from ....conductor.src.hooks.secure_resource import Secure, NotEnoughPrivileges, NotAuthorizedError
from ....storage.builtin_datasets import BuiltinDataset
from ....conductor.src.auth_models import User, Role


@pytest.fixture
def prepared_data():
    """ Prepare user and roles for authentification """
    dataset = BuiltinDataset("", from_file=False)
    role = Role(dataset).add_role("User", 0)
    bigger_role = Role(dataset).add_role("Admin", 1)
    user = User(dataset).store_user("admin", "Pass1234", "User")
    return (dataset, role, user)


@pytest.fixture
def request_mock(prepared_data):
    """ Prepare mock for Request """
    mock = MagicMock()
    mock.context.user = prepared_data[2]
    return mock


def test_secure_should_raise_NotAuthorizedError_if_no_user_in_request_context(request_mock):
    """ Secure should raise NotAuthorizedError when no user found """
    secure_hook = Secure()
    request_mock.context.user = None
    with pytest.raises(NotAuthorizedError):
        secure_hook(request_mock, MagicMock(), MagicMock(), MagicMock())

def test_secure_should_raise_NotEnoughPrivileges_if_role_with_higher_rank_required(request_mock):
    """ Secure should raise NotEnoughPrivileges when user role has smaller rank, than the one that needed """
    secure_hook = Secure("Admin")
    with pytest.raises(NotEnoughPrivileges):
        secure_hook(request_mock, MagicMock(), MagicMock(), MagicMock())
