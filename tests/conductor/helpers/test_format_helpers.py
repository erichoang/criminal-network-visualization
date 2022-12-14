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

 Unit tests for string formatters """
from uuid import uuid4
from datetime import datetime
from conductor.src.helpers.format_helpers import timestamp_format, log_format


def test_timestamp_format_should_convert_datetime_to_rfc_5322_timestamp():
    """ timestamp format should format datetime to RFC 5322 GMT timestamp """
    timestamp = datetime(2020, 2, 1, 22, 15, 13)
    expected_timestamp = "Sat, 1 Feb 2020 22:15:13 GMT"
    assert timestamp_format(timestamp) == expected_timestamp


def test_log_format_should_format_args_in_logfmt():
    """ log_format should return string in logfmt format """
    request_id = str(uuid4())
    message = "Request made"
    params = {"data": "foo"}
    expected_message = f'request_id="{request_id}" message="{message}" data="{params["data"]}"'
    formatted_message = log_format(request_id, message, params)
    assert expected_message == formatted_message
