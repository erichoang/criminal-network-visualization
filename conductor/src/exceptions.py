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

 Common application exceptions """
from uuid import uuid4
from collections import namedtuple
from falcon import HTTPError, HTTP_400, HTTP_500, HTTP_401, HTTP_404, HTTP_409

ErrorDetail = namedtuple("ErrorDetail", ["code", "target", "message"])


class APIError(RuntimeError):
    """ Common API exception """

    code = "APIError"
    response_code = HTTP_500

    def __init__(self, message, target, details=None):
        self.message = message
        self.target = target
        self.details = details

    @classmethod
    def from_http_error(cls, ex: HTTPError):
        """ Create exception class from falocn HTTPError """
        error = cls(ex.title, "HTTP request")
        error.response_code = ex.status
        return error

    @classmethod
    def to_docs_example(cls, message=None, target=None, details=None):
        """ Create Swagger doc form exception """
        return {
            "request_id": str(uuid4()),
            "code": cls.code,
            "message": message if message else "Message here",
            "target": target if target else "Error target",
            "details": details if details else []
        }

    def to_dict(self, request_id: str):
        """ Return dict to be serialized """
        result = {
            "request_id": request_id,
            "code": self.code,
            "message": self.message,
            "target": self.target
        }
        if self.details:
            result["details"] = [{"code": d.code, "target": d.target, "message": d.message} for d in self.details]
        return result

    def __str__(self):
        return self.message


class VersioningError(APIError):
    """ Error with api verion given """
    code = "VersioningError"
    response_code = HTTP_400


class TaskError(APIError):
    """ Error in task preparation or execution """
    code = "TaskError"
    response_code = HTTP_409


class AuthenticationError(APIError):
    """ Error in login, account creation or access verification """
    code = "AuthenticationError"
    response_code = HTTP_401


class ValidationError(APIError):
    """ Error validating user input """
    code = "ValidationError"
    response_code = HTTP_400


class ResourceError(APIError):
    """ Resource either does not exists or unavalible """
    code = "ResourceError"
    response_code = HTTP_404


class FormValidationError(ValidationError):
    """ Error validating form input """
    code = "FormValidationError"
    response_code = HTTP_400


class FileNotFoundError(APIError):
    """ Error finding file """
    code = "FileNotFoundError"
    response_code = HTTP_404


class DatasetError(APIError):
    """ Error within dataset """
    code = "DatasetError"
    response_code = HTTP_500

    @classmethod
    def from_dataset_message(cls, dataset_message):
        """ Create error from dataset message """
        return cls(dataset_message["message"], "dataset")
