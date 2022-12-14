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

 FormComponent tests  """
import pytest
from io import BytesIO
from unittest.mock import MagicMock, patch
from ....conductor.src.middlewares.multipart import FormComponent


@pytest.fixture
def prepared_request():
    """ Set multipart request """
    request = MagicMock()
    request.stream = BytesIO(b"form")
    request.content_type = "multipart/form-data"
    request.env = MagicMock()
    return request

def test_form_component_should_process_request_stream_as_FieldStorage(prepared_request):
    """ FormComponent should take Request.stream and read it with cgi.FieldStorage if content-type is 'multipart/form-data'"""
    with patch("cgi.FieldStorage") as field_mock:
        form_storage = MagicMock()
        field_mock.return_value = form_storage
        middleware = FormComponent()
        middleware.process_request(prepared_request, MagicMock())
        assert prepared_request.context.form == form_storage


def test_form_component_should_set_request_context_form_with_FieldStorage(prepared_request):
    """ FormComponent should take Request.stream and read it with cgi.FieldStorage and put it in Request.context.form if content-type is 'multipart/form-data'"""
    with patch("cgi.FieldStorage") as field_mock:
        middleware = FormComponent()
        middleware.process_request(prepared_request, MagicMock())
        field_mock.assert_called_once_with(fp=prepared_request.stream, environ=prepared_request.env, keep_blank_values=1)
