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

 Collection resource for datasets """
from os import remove
from falcon import Request, Response, before, HTTP_200, HTTP_201
from werkzeug.utils import secure_filename
from ..hooks.secure_resource import Secure
from ..helpers.file_helpers import save_file
from ..helpers.validate_schema import validate_schema
from ..schemas.datasets_collection_schemas import list_datasets, create_dataset, delete_dataset
from ..exceptions import FormValidationError
from ..helpers.log_helpers import log_event


@before(Secure("User"))
class DatasetsCollectionResource(object):
    """
    summary: Dataset collection resource
    description: Allows listing datasets or creating new dataset
    """

    @validate_schema(output_schema=list_datasets)
    def on_get_v1_0(self, req: Request, resp: Response):
        """
        summary: List datasets
        externalDocs:
            description: Example of listing user datasets
            url: /docs/api_examples.html#list_datasets
        responses:
            200:
                description: If user has any datasets, they will be listed
                content:
                    application/json:
                        schema: ListDatasets
                        examples: DatasetCollectionGetExample
                    application/msgpack:
                        schema: ListDatasets
                        examples: DatasetCollectionGetExample
        security:
            - jwt:
                - User
        examples:
            - ex_name: DatasetCollectionGetExample
              datasets:
                - TestDataset
        """
        resp.media = {
            "datasets": req.context.user.list_datasets()
        }
        resp.status = HTTP_200
        log_event(req.context.request_id, "User's datasets listed")

    def handle_form_post(self, form, user):
        """ Handle dataset creation from form """
        try:
            filename = secure_filename(form["file"].filename)
            filepath = user.get_folder_path() / filename
            save_file(form["file"].file, filepath)
            user.create_dataset(
                form["datasetName"].value,
                form.getvalue("datasetDescription", ""),
                filename,
                True
            )
            remove(filepath)
        except KeyError as err:
            raise FormValidationError(f"Form key not found: {err.args[0]}", "form")

    @validate_schema(create_dataset)
    def on_post_v1_0(self, req: Request, resp: Response):
        """
        summary: Create new dataset from file or dump dataset into a file
        description: If dumpFile is in the request body dataset will be dumped
        externalDocs:
            description: Examples of post requests in python
            url: /docs/api_examples.html#datasets_post
        requestBody:
            description: New dataset info
            content:
                application/json:
                    schema: CreateDataset
                    examples:
                        - DatasetCollectionPostFileCreate
                        - DatasetCollectionPostFileDump
                application/msgpack:
                    schema: CreateDataset
                    examples:
                        - DatasetCollectionPostFileCreate
                        - DatasetCollectionPostFileDump
                multipart/form-data:
                    schema:
                        type: object
                        properties:
                            datasetName:
                                type: string
                            datasetDescription:
                                type: string
                            file:
                                type: string
                                format: binary
                    encoding:
                        file:
                            contentType: application/json
                    examples: DatasetCollectionPostFileUpload
        responses:
            201:
                description: Successful dataset creation or dumping
                headers:
                    Location:
                        description: Relative path to new dataset or dumped file location
                        schema:
                            type: string
        security:
            - jwt:
                - User
        errors:
            - name: FileExistsError
              message: File already exists!
              target: filename
            - name: FormValidationError
              message: "Form key not found: ..."
              target: form
            - name: DatasetCreationError
              message: dataset_id is already existed
              target: dataset
            - name: DatasetCreationError
              message: there should be some error in IO
              target: dataset
            - name: DatasetDoesNotExistError
              message: "Couldn't find dataset by name ..."
              target: dataset name
        examples:
            - ex_name: DatasetCollectionPostFileUpload
              datasetName: TestDataset
              datasetDescription: Dataset to make an example
              file: {}
            - ex_name: DatasetCollectionPostFileCreate
              datasetName: TestDataset
              datasetDescription: Dataset to make an example
              uploadFile: temp.json
            - ex_name: DatasetCollectionPostFileDump
              datasetName: TestDataset
              dumpFile: temp.json
        """
        if hasattr(req.context, "form"):
            self.handle_form_post(req.context.form, req.context.user)
            resp.status = HTTP_201
            resp.set_header("Location", "/v1.0/datasets/" + req.context.form["datasetName"].value)
            log_event(
                req.context.request_id,
                "Dataset created from posted file",
                dataset=req.context.form["datasetName"].value)
            return
        if req.media.get("dumpFile"):
            dataset = req.context.user.get_dataset(req.media["datasetName"])
            dataset.dump_network(req.media["dumpFile"], str(req.context.user.get_folder_path()))
            resp.status = HTTP_201
            resp.set_header("Location", "/v1.0/files/" + req.media["dumpFile"])
            log_event(
                req.context.request_id,
                "Dataset dumped into a file",
                dataset=req.media["dumpFile"],
                file=req.media["dumpFile"])
            return
        if req.media.get("uploadFile"):
            req.context.user.create_dataset(
                req.media["datasetName"],
                req.media["datasetDescription"] if req.media.get("datasetDescription") else "",
                secure_filename(req.media["uploadFile"]),
                True
            )
            log_event(
                req.context.request_id,
                "Dataset created from file in user's folder",
                dataset=req.media["datasetName"],
                file=req.media["uploadFile"])
        else:
            req.context.user.create_dataset(
                req.media["datasetName"],
                req.media["datasetDescription"] if req.media.get("datasetDescription") else "",
                None
            )
            log_event(
                req.context.request_id,
                "Created empty dataset",
                dataset=req.media["datasetName"])
        resp.status = HTTP_201
        resp.set_header("Location", "/v1.0/datasets/" + req.media["datasetName"])

    @validate_schema(delete_dataset)
    def on_delete_v1_0(self, req: Request, resp: Response):
        """
        summary: Remove dataset
        externalDocs:
            description: Example of deleting dataset
            url: /docs/api_examples.html#datasets_delete
        requestBody:
            description: Name of the dataset to delete
            content:
                application/json:
                    schema: DeleteDataset
                    examples: DatasetCollectionDeleteRequest
                application/msgpack:
                    schema: DeleteDataset
                    examples: DatasetCollectionDeleteRequest
        responses:
            200:
                description: Dataset successfuly deleted
        security:
            - jwt:
                - User
        errors:
            - name: DatasetRemovalError
              message: "Couldn't find dataset by name ..."
              target: dataset
        examples:
            - ex_name: DatasetCollectionDeleteRequest
              datasetName: TestDataset
        """
        req.context.user.remove_dataset(req.media["datasetName"])
        resp.status = HTTP_200
        log_event(
            req.context.request_id,
            "Dataset removed",
            dataset=req.media["datasetName"])
