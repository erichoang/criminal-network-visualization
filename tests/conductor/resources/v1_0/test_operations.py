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

 Test opeartions resource """
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from falcon.testing import TestClient
from conductor.src.auth_models import User


def test_operations_resource_should_get_task_data_if_it_is_successful(client: TestClient, prepared_header, prepared_user: User):
    """ get request on operations resource should return operation result if it is completed successfully """
    task_response = {
        "createdDateTime": str(datetime.now()),
        "lastActionDateTime": str(datetime.now()),
        "status": "SUCCESS",
        "description": "Analysis resulted successfully",
        "result": {}
    }
    with patch("conductor.src.resources.operations.celery") as celery_mock:
        result_mock = MagicMock()
        result_mock.ready.return_value = True
        result_mock.get.return_value = task_response
        celery_mock.AsyncResult.return_value = result_mock
        result = client.simulate_get("/v1.0/operations/pepe", headers=prepared_header)
        assert result.json["taskData"] == task_response
        assert result.status_code == 200


def test_operations_resource_should_return_info_if_task_is_not_ready(client: TestClient, prepared_header, prepared_user: User):
    """ get request on operations resource should return info if task.ready is false """
    task_response = {
        "createdDateTime": str(datetime.now()),
        "lastActionDateTime": str(datetime.now()),
        "status": "RUNNING",
        "description": "Running task",
        "result": {}
    }
    with patch("conductor.src.resources.operations.celery") as celery_mock:
        result_mock = MagicMock()
        result_mock.ready.return_value = False
        result_mock.info = task_response
        celery_mock.AsyncResult.return_value = result_mock
        result = client.simulate_get("/v1.0/operations/pepe", headers=prepared_header)
        assert result.json["taskData"] == task_response
        assert result.status_code == 200


def test_operations_should_forget_task_if_delete_request_issued(client: TestClient, prepared_header, prepared_user: User):
    """ delete request on operations resource should call forget() method on task """
    with patch("conductor.src.resources.operations.celery") as celery_mock:
        result_mock = MagicMock()
        celery_mock.AsyncResult.return_value = result_mock
        result = client.simulate_delete("/v1.0/operations/pepe", headers=prepared_header)
        result_mock.forget.assert_called_once()
        assert result.status_code == 200
