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

 Route to manage files """
import mimetypes
from os.path import getsize, isfile
from os import remove
from falcon import Request, Response, before, HTTP_200, HTTP_201
from werkzeug.utils import secure_filename
from ..hooks.secure_resource import Secure
from ..helpers.file_helpers import save_file, stream_file
from ..exceptions import FileNotFoundError, FormValidationError, ValidationError
from ..helpers.log_helpers import log_event


@before(Secure("User"))
class FilesResource(object):
    """
    summary: File Resource
    description: Allows managing files in the users folder
    """

    def on_get_v1_0(self, req: Request, resp: Response, filename):
        """
        summary: Download a file
        externalDocs:
            description: Example of downloading a file
            url: /docs/api_examples.html#file_download
        parameters:
            -   in: path
                name: filename
                required: true
                schema:
                    type: string
                description: Name of the file
        responses:
            200:
                description: Stream of file contents
                content:
                    "*/*":
                        schema:
                            type: string
                            format: binary
        security:
            - jwt:
                - User
        errors:
            - name: FileNotFoundError
              message: "File ... not found!"
              target: url path
        """
        secure_name = secure_filename(filename)
        filepath = req.context.user.get_folder_path() / secure_name
        if not isfile(filepath):
            raise FileNotFoundError(f"File {secure_name} not found!", "url path")
        resp.content_length = getsize(filepath)
        resp.stream = stream_file(filepath)
        resp.content_type = mimetypes.guess_type(secure_name)[0]
        resp.status = HTTP_200
        log_event(
            req.context.request_id,
            "File prepared for download",
            file=secure_name,
            size=resp.content_length)

    def on_post_v1_0(self, req: Request, resp: Response, filename):
        """
        summary: Upload a file
        externalDocs:
            description: Example of uploading a file
            url: /docs/api_examples.html#file_upload
        parameters:
            -   in: path
                name: filename
                required: true
                schema:
                    type: string
                description: Name of the file
        requestBody:
            description: File contents
            content:
                multipart/form-data:
                    schema:
                        type: object
                        properties:
                            file:
                                type: string
                                format: binary
                    encoding:
                        file:
                            contentType: application/json
                    examples: FilePostUploadFileExample
        responses:
            201:
                description: File was successfuly uploaded
                headers:
                    Location:
                        description: Relative path to uploaded file
                        schema:
                            type: string
        security:
            - jwt:
                - User
        errors:
            - name: ValidationError
              message: File form not found
              target: request body
            - name: FormValidationError
              message: "Field 'file' not found"
              target: form
            - name: FileExistsError
              message: File already exists!
              target: filename
        examples:
            - ex_name: FilePostUploadFileExample
              file: {}
        """
        if not hasattr(req.context, "form"):
            raise ValidationError("File form not found", "request body")
        file = None
        try:
            file = req.context.form["file"]
        except KeyError:
            raise FormValidationError("Field 'file' not found", "form")
        secure_name = secure_filename(filename)
        filepath = req.context.user.get_folder_path() / secure_name
        save_file(file.file, filepath)
        resp.set_header("Location", "/v1.0/files/" + secure_name)
        resp.status = HTTP_201
        log_event(
            req.context.request_id,
            "File uploaded",
            file=secure_name)

    def on_put_v1_0(self, req: Request, resp: Response, filename):
        """
        summary: Upload or replace a file
        externalDocs:
            description: Example of replacing a file
            url: /docs/api_examples.html#file_replace
        parameters:
            -   in: path
                name: filename
                required: true
                schema:
                    type: string
                description: Name of the file
        requestBody:
            description: File contents
            content:
                multipart/form-data:
                    schema:
                        type: object
                        properties:
                            file:
                                type: string
                                format: binary
        responses:
            201:
                description: File was successfuly uploaded
                headers:
                    Location:
                        description: Relative path to uploaded file
                        schema:
                            type: string
            200:
                description: File was successfuly replaced
        security:
            - jwt:
                - User
        errors:
            - name: ValidationError
              message: File form not found
              target: request body
            - name: FormValidationError
              message: Field 'file' not found
              target: form
        examples:
            - ex_name: FilePutReplaceExample
              file: {}
        """
        if not hasattr(req.context, "form"):
            raise ValidationError("File form not found", "request body")
        file = None
        try:
            file = req.context.form["file"]
        except KeyError:
            raise FormValidationError("Field 'file' not found", "form")
        secure_name = secure_filename(filename)
        filepath = req.context.user.get_folder_path() / secure_name
        log_message = None
        if isfile(filepath):
            remove(filepath)
            resp.status = HTTP_200
            log_message = "File replaced"
        else:
            resp.status = HTTP_201
            resp.set_header("Location", "/v1.0/files/" + secure_name)
            log_message = "File uploaded"
        save_file(file.file, filepath)
        log_event(
            req.context.request_id,
            log_message,
            file=secure_name)

    def on_delete_v1_0(self, req: Request, resp: Response, filename):
        """
        summary: Remove a file
        externalDocs:
            description: Example of deleting a file
            url: /docs/api_examples.html#file_delete
        parameters:
            -   in: path
                name: filename
                required: true
                schema:
                    type: string
                description: Name of the file
        responses:
            200:
                description: File was removed
        security:
            - jwt:
                - User
        errors:
            - name: FileNotFoundError
              message: File ... not found!
              target: url path
        """
        secure_name = secure_filename(filename)
        filepath = req.context.user.get_folder_path() / secure_name
        if not isfile(filepath):
            raise FileNotFoundError(f"File {secure_name} not found!", "url path")
        remove(filepath)
        resp.status = HTTP_200
        log_event(
            req.context.request_id,
            "File removed",
            file=secure_name)
