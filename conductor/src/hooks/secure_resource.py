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

 Add roule authorization to the recource """
from falcon import Request, Response, HTTP_401, HTTP_403
from ..auth_graph import auth_dataset
from ..auth_models import Role
from ..exceptions import AuthenticationError, ErrorDetail


class NotAuthorizedError(AuthenticationError):
    """ Error authorizing user """
    code = "NotAuthorizedError"
    response_code = HTTP_401


class NotEnoughPrivileges(AuthenticationError):
    """ User does not have enough privileges to access the recource """
    code = "NotEnoughPrivileges"
    response_code = HTTP_403


class Secure(object):
    """ Authoroze user and check proper role if given """

    def __init__(self, role=None):
        self.role_name = role

    def __call__(self, request: Request, response: Response, resource, params):
        """
        Check user auhorization in request

        :param request: falcon.Request
        :param response: falcon.Response
        :param resource: Resource class
        :param params: url params
        """
        if not request.context.user:
            raise NotAuthorizedError("Authorization required to access the recourse", "Authentication header")
        if not self.role_name:
            return
        user_role = request.context.user.get_role()
        role = Role(auth_dataset).get_role_vertex(self.role_name)
        if user_role.get_rank() < role.get_rank():
            description = ErrorDetail("RequiredRole", "role", role.get_name())
            raise NotEnoughPrivileges("Not enough privileges to access the recourse", "User role", [description])
