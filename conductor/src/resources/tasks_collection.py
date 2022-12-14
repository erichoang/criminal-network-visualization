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

 Analysis algorithms collection resource """
from falcon import Request, Response, before, HTTP_200
from ..hooks.secure_resource import Secure
from ..helpers.validate_schema import validate_schema
from ..schemas.tasks_collection_schemas import list_algorithms_schema
from analyzer import request_taker
from ..helpers.log_helpers import log_event


@before(Secure("User"))
class TasksCollectonResource(object):
    """
    summary: Tasks Collection Resource
    description: Allows listing of analysis algorithms
    """

    @validate_schema(output_schema=list_algorithms_schema)
    def on_get_v1_0(self, req: Request, resp: Response):
        """
        summary: List Avalible Algorithms
        externalDocs:
            description: Example of listing the algorithms
            url: /docs/api_examples.html#list_algorithms
        responses:
            200:
                description: List of all avalible algorithms with their parameters
                content:
                    application/json:
                        schema: ListAlgorithmsSchema
                        examples: TaskGetRequestExample
                    application/msgpack:
                        schema: ListAlgorithmsSchema
                        examples: TaskGetRequestExample
        security:
            - jwt:
                - User
        examples:
            - ex_name: TaskGetRequestExample
              tasks:
                - name: community_detection
                  methods:
                    - name: k_cliques
                      description: K-clique
                      parameter:
                        - K:
                            description: Size of smallest clique
                            options:
                                Integer:
                                    - 3
                                    - 4
                                    - 5
                                    - 6
                                    - 7
        """
        algorithm_info = request_taker.get_info()
        response = {
            "tasks": []
        }
        for a in algorithm_info:
            temp_algorithm = {
                "name": a,
                "methods": []
            }
            for m in algorithm_info[a]["methods"]:
                temp_algorithm["methods"].append({
                    "name": m,
                    "description": algorithm_info[a]["methods"][m]["name"],
                    "parameter": algorithm_info[a]["methods"][m]["parameter"]
                })
            response["tasks"].append(temp_algorithm)
        resp.media = response
        resp.status = HTTP_200
        log_event(req.context.request_id, "Avalible algorithms listed")
