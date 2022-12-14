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

 Tests for validate_schema decorator """
import pytest
from unittest.mock import MagicMock, Mock
from falcon import Request
from ....conductor.src.helpers.validate_schema import validate_schema, InputMachingError, OutputMatchingError

@pytest.fixture
def request_mock():
    request = MagicMock()
    request.media = {
        "key": "val"
    }
    del request.context.form
    return request

def test_validate_schema_should_validate_dictonary_data_in_request_media(request_mock):
    """ validate_schema should decorate request handler with function, that will walidate Request.media agains given schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        },
        "required": ["key"]
    }
    @validate_schema(schema)
    def func(self, req, resp):
        assert req.media == {"key": "val"}
    func(MagicMock(), request_mock, MagicMock())

def test_validate_schema_should_raise_InputMachingError_if_schema_not_matched(request_mock):
    """ validate_schema should decorate request handler with function, that raises InputMachingError if Request.media does not match schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "number"},
            "field": {"type": "number"}
        }
    }
    @validate_schema(schema)
    def func(self, req, resp):
        pass
    with pytest.raises(InputMachingError):
        func(MagicMock(), request_mock, MagicMock())

def test_validate_schema_should_validate_dictonary_data_in_response_media(request_mock):
    """ validate_schema should decorate request handler with function, that will walidate Request.media agains given schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "field": {"type": "number"}
        }
    }
    out_schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        },
        "required": ["key"]
    }
    response_mock = MagicMock()
    @validate_schema(schema, out_schema)
    def func(self, req, resp):
        resp.media = req.media
    func(MagicMock(), request_mock, response_mock)
    assert response_mock.media == request_mock.media

def test_validate_schema_should_raise_OutputMatchingError_if_output_schema_not_matched(request_mock):
    """ validate_schema should decorate request handler with function, that raises OutputMatchingError if Response.media does not match schema """
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        }
    }
    out_schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "field": {"type": "number"}
        },
        "required": ["key", "field"]
    }
    out_mock = MagicMock()
    out_mock.stream = None
    @validate_schema(schema, out_schema)
    def func(self, req, resp):
        resp.media = req.media
    with pytest.raises(OutputMatchingError):
        func(MagicMock(), request_mock, out_mock)
