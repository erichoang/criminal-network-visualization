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

 Resource to authenticate user """
from falcon import Request, Response, HTTP_200
from ..helpers.validate_schema import validate_schema
from ..helpers.auth_helpers import create_token
from ..schemas.login_schemas import login_request, login_response
from ..auth_models import User
from ..auth_graph import auth_dataset
from ..helpers.log_helpers import log_event


class LoginResource(object):
    """
    summary: Login Resource
    description: Provides login into account
    """

    @validate_schema(login_request, login_response)
    def on_post_v1_0(self, req: Request, resp: Response):
        """
        summary: Log In
        externalDocs:
            description: Example of logging in
            url: /docs/api_examples.html#login
        requestBody:
            description: User's credentials
            content:
                application/json:
                    schema: LoginRequest
                    examples: LoginRequestExample
                application/msgpack:
                    schema: LoginRequest
                    examples: LoginRequestExample
        responses:
            200:
                description: After successfull login access token will be provided
                content:
                    application/json:
                        schema: LoginResponse
                    application/msgpack:
                        schema: LoginResponse
        errors:
            - name: AuthRecordNotFoundError
              message: User by username ... not found!
              target: username
            - name: WrongPasswordError
              message: Wrong password!
              target: User
        examples:
            - ex_name: LoginRequestExample
              username: admin
              password: Pass1234
        """
        user = User(auth_dataset).authenticate(req.media["username"], req.media["password"])
        access_token = create_token({"username": user.get_username()})
        resp.media = {"accessToken": access_token}
        resp.status = HTTP_200
        log_event(
            req.context.request_id,
            "Successfull login",
            username=req.media["username"])
