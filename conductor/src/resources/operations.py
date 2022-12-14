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

 Resource to manage long-running operations """
from falcon import Request, Response, before, HTTP_200
from ..helpers.validate_schema import validate_schema
from ..schemas.operations_schemas import get_response
from ..hooks.secure_resource import Secure
from ..celery import celery
from ..helpers.log_helpers import log_event


@before(Secure("User"))
class OperationsResource(object):
    """
    summary: Operations Resource
    description: Resource for managing the tasks submitted for processing
    """

    @validate_schema(output_schema=get_response)
    def on_get_v1_0(self, req: Request, resp: Response, operation_id):
        """
        summary: Get update on task state
        externalDocs:
            description: Example of getting task result
            url: /docs/api_examples.html#get_operation
        parameters:
            -   in: path
                name: operation_id
                required: true
                schema:
                    type: string
                description: ID of the task
        responses:
            200:
                description: Task state
                content:
                    application/json:
                        schema: OperationUpdate
                        examples: OperationGetResponseExample
                    application/msgpack:
                        schema: OperationUpdate
                        examples: OperationGetResponseExample
        security:
            - jwt:
                - User
        errors:
            - name: TaskError
              message: Error message of task exception
              target: Task
        examples:
            - ex_name: OperationGetResponseExample
              taskData:
                createdDateTime: Fri, 21 Aug 2020 14:55:25 GMT
                lastActionDateTime: Fri, 21 Aug 2020 14:55:30 GMT
                status: SUCCESS
                description: Analysis resulted successfuly
                result:
                    scores:
                        Yayha_al_Azari: 0.221
                        Omar_al_Shishani: 0.084
        """
        task = celery.AsyncResult(operation_id)
        resp.media = {
            "taskData": task.get() if task.ready() else task.info
        }
        resp.status = HTTP_200
        log_event(
            req.context.request_id,
            "Operation status returned",
            operation=operation_id)

    def on_delete_v1_0(self, req: Request, resp: Response, operation_id):
        """
        summary: Forget task
        externalDocs:
            description: Example of deleting operation
            url: /docs/api_examples.html#forget_operation
        parameters:
            -   in: path
                name: operation_id
                required: true
                schema:
                    type: string
                description: ID of the task
        responses:
            200:
                description: Terminate and remove task
        security:
            - jwt:
                - User
        """
        task = celery.AsyncResult(operation_id)
        task.forget()
        resp.status = HTTP_200
        log_event(
            req.context.request_id,
            "Operation removed",
            operation=operation_id)
