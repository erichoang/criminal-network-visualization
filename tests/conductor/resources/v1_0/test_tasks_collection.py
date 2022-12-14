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

 Unit tests for algorithms collection """
import pytest
from unittest.mock import patch
from falcon import HTTP_201
from falcon.testing import TestClient
from conductor.src.auth_models import User


def test_algorithms_resource_should_return_algorithm_info_on_get_request(client: TestClient, prepared_header, prepared_user: User):
    """ get request on algorithms resource should return edited analyzer info """
    example_info = {
        "community_detection": {
            "methods": {
                "asyn_lpa": {
                    "name": "Asynchronous Label Propagation",
                    "parameter": {}
                }
            }
        },
        "node_embedding": {
            "methods": {
                "nmf": {
                    "name": "Non-negative Matrix Factorization",
                    "parameter": {
                        "K": {
                            "description": "The embedding dimension",
                            "options": {
                                "Integer": "Integer"
                            }
                        }
                    }
                }
            }
        }
    }
    expected_info = {
        "tasks": [
            {
                "name": "community_detection",
                "methods": [
                    {
                        "name": "asyn_lpa",
                        "description": "Asynchronous Label Propagation",
                        "parameter": {}
                    }
                ]
            },
            {
                "name": "node_embedding",
                "methods": [
                    {
                        "name": "nmf",
                        "description": "Non-negative Matrix Factorization",
                        "parameter": {
                            "K": {
                                "description": "The embedding dimension",
                                "options": {
                                    "Integer": "Integer"
                                }
                            }
                        }
                    }
                ]
            }
        ]
    }
    with patch("conductor.src.resources.tasks_collection.request_taker") as analyzer_mock:
        analyzer_mock.get_info.return_value = example_info
        result = client.simulate_get("/v1.0/tasks", headers=prepared_header)
        assert result.json == expected_info
