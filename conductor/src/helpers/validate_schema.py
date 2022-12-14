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

 Use fastjsonschema validation """
from functools import wraps
from falcon import HTTP_400, HTTP_500
import fastjsonschema
from fastjsonschema.exceptions import JsonSchemaException
from ..exceptions import ValidationError, ErrorDetail


class InputMachingError(ValidationError):
    """ Error validationg input against schema """
    code = "InputMachingError"
    response_code = HTTP_400


class OutputMatchingError(ValidationError):
    """ Error validating output against schema """
    code = "OutputMatchingError"
    response_code = HTTP_500


def validate_schema(input_schema=None, output_schema=None):
    """
    Validate schema and raise appropriate exceptions if validation fails

    :param input_schema: schema, that will validate media in Request
    :returns: decorated function
    """
    input_validator = fastjsonschema.compile(input_schema) if input_schema else None
    output_validator = fastjsonschema.compile(output_schema) if output_schema else None

    def check_role(route):
        @wraps(route)
        def intermediate(*args, **kwargs):
            try:
                if input_validator and not hasattr(args[1].context, "form"):  # skip form data
                    input_validator(args[1].media)
            except JsonSchemaException as ex:
                definition_detail = ErrorDetail("UnmatchedSchema", input_schema, "Failed validation schema")
                raise InputMachingError(ex.message, "request body", [definition_detail])
            response = route(*args, **kwargs)
            try:
                if output_validator and not args[2].stream:  # skip files
                    output_validator(args[2].media)
            except JsonSchemaException as ex:
                definition_detail = ErrorDetail("UnmatchedSchema", output_schema, "Failed output validation schema")
                output_detail = ErrorDetail("UnmatchedOutput", args[2].media, "Failed output")
                raise OutputMatchingError(ex.message, "request body", [definition_detail, output_detail])
            return response
        return intermediate
    return check_role
