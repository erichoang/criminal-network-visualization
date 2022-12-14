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

 Handle API errors """
from traceback import format_tb
from falcon import (
    HTTPError,
    Request,
    Response)
from .. import api
from .exceptions import APIError, ErrorDetail
from .helpers.log_helpers import log_error, log_exception


def hanlde_errors(request: Request, response: Response, exception: HTTPError, params):
    """ Create API error responses """
    if issubclass(exception.__class__, HTTPError):
        exception = APIError.from_http_error(exception)
    response.status = exception.response_code
    response.media = exception.to_dict(request.context.request_id)
    log_error(request.context.request_id, exception)


def handle_any_error(req: Request, resp: Response, exception: Exception, params):
    """ Handle server errors """
    traceback = "".join(format_tb(exception.__traceback__))
    traceback_detail = ErrorDetail("ExceptionTraceback", "code", traceback)
    error = APIError(str(exception), "api", [traceback_detail])
    resp.status = error.response_code
    resp.media = error.to_dict(req.context.request_id)
    log_exception(req.context.request_id, error.message, traceback)


api.add_error_handler(Exception, handle_any_error)
api.add_error_handler([HTTPError, APIError], hanlde_errors)
