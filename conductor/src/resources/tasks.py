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

 Resource for algorithm tasks """
import ujson
from datetime import datetime, timezone
from falcon import Request, Response, before, HTTP_202
from werkzeug.utils import secure_filename
from ..hooks.secure_resource import Secure
from ..helpers.validate_schema import validate_schema
from ..helpers.file_helpers import save_file
from ..helpers.network_helpers import network_to_split
from ..helpers.format_helpers import timestamp_format
from ..helpers.task_helpers import generate_response, save_form_file
from ..exceptions import ValidationError, FormValidationError
from ..schemas.tasks_schemas import post_input
from ..tasks.celery_tasks import perform_analysis_file, perform_analysis_network
from storage.builtin_datasets import BuiltinDataset
from ..helpers.log_helpers import log_event


@before(Secure("User"))
class TaskResource(object):
    """
    summary: Tasks Resource
    description: Allows submission of analysis tasks
    """

    def handle_form(self, form, task_name, req: Request, resp: Response):
        """ Handle file form to create an analysis task"""
        try:
            filepath = save_form_file(req.context.form, req.context.user.get_folder_path())
            task_result = None
            options = ujson.loads(form["options"].value)
            parameters = ujson.loads(form["parameters"].value) if "parameters" in form else None
            task_result = perform_analysis_file.delay(
                filepath,
                task_name,
                options,
                timestamp_format(datetime.now(timezone.utc)),
                parameters
            )
            generate_response(resp, task_result.id)
            log_event(
                req.context.request_id,
                "Analysis task dispatched from uploaded file",
                id=task_result.id,
                file=filepath)
        except KeyError as err:
            raise FormValidationError(f"Form key not found: {err.args[0]}", "form")
        except ValueError:
            raise ValidationError("options and parameters form fields must contain valid json!", "form")

    @validate_schema(post_input)
    def on_post_v1_0(self, req: Request, resp: Response, task_name):
        """
        summary: Submit new task
        externalDocs:
            description: Example python code to make tasks
            url: /docs/api_examples.html#tasks
        parameters:
            -   in: path
                name: task_name
                required: true
                schema:
                    type: string
                description: Name of the task
        requestBody:
            description: Task data
            content:
                application/json:
                    schema: TaskInput
                    examples:
                        - TaskPostRequestAnalyzeNetworkExample
                        - TaskPostRequestAnalyzeNetworkDatasetExample
                application/msgpack:
                    schema: TaskInput
                    examples:
                        - TaskPostRequestAnalyzeNetworkExample
                        - TaskPostRequestAnalyzeNetworkDatasetExample
                multipart/form-data:
                    schema:
                        type: object
                        properties:
                            file:
                                type: string
                                format: binary
                            options:
                                type: object
                                properties:
                                    method:
                                        type: string
                                    parameters:
                                        type: object
                            parameters:
                                type: object
                    encoding:
                        file:
                            contentType: application/json
                    examples:
                        - TaskPostRequestAnalyzeFormExample
        responses:
            202:
                description: Task submitted
                headers:
                    Operation-Location:
                        description: Relative path to the newly submitted task
                        schema:
                            type: string
        security:
            - jwt:
                - User
        errors:
            - name: ValidationError
              message: No task creation method provided
              target: request body
            - name: ValidationError
              message: "'options' field required for analysis"
              target: request body
            - name: FileExistsError
              message: File already exists!
              target: filename
            - name: FormValidationError
              message: "Form key not found: key"
              target: form
            - name: FormValidationError
              message: options and parameters form fields must contain valid json!
              target: form
            - name: FormValidationError
              message: file field not found
              target: format
        examples:
            - ex_name: TaskPostRequestAnalyzeFormExample
              summary: Create analysis task by uploading a file
              file: {}
              options: {"method": "authority", "parameters": {}}
            - ex_name: TaskPostRequestAnalyzeNetworkExample
              summary: Create analysis task with passed network
              network:
                - type: node
                  id: eddiewillows
                  properties:
                    type: person
                    name: eddiewillows
                - type: edge
                  source: eddiewillows
                  target: shibley
                  properties:
                    type: conversations
                    observes: true
                    weight: 1
              options:
                method: authority
                parameters: {}
            - ex_name: TaskPostRequestAnalyzeNetworkDatasetExample
              summary: Analyze network from a dataset
              dataset: TestDataset
              options:
                method: authority
                parameters: {}
        """
        if hasattr(req.context, "form"):
            self.handle_form(req.context.form, task_name, req, resp)
            return
        dataset = None
        log_message = None
        if req.media.get("network"):
            dataset = BuiltinDataset(None, from_file=False)
            network_split = network_to_split(req.media["network"])
            dataset.save_nodes({n["id"]: n["properties"] for n in network_split["nodes"]})
            dataset.save_edges(network_split["edges"])
            log_message = "Analysis task dispatched from provided network"
        elif req.media.get("dataset"):
            dataset = req.context.user.get_dataset(req.media["dataset"])
            log_message = "Analysis task dispatched from user dataset"
        else:
            raise ValidationError("No task creation method provided", "request body")
        if not req.media.get("options"):
            raise ValidationError("'options' field required for analysis", "request body")
        task_result = perform_analysis_network.delay(
            {
                "task_id": task_name,
                "network": dataset.get_network(),
                "options": req.media["options"]
            },
            timestamp_format(datetime.now(timezone.utc)),
            req.media.get("parameters")
        )
        generate_response(resp, task_result.id)
        log_event(req.context.request_id, log_message, id=task_result.id)
