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

 Resource to manage allo of users """
from falcon import Request, Response, before, HTTP_200, HTTP_201
from ..hooks.secure_resource import Secure
from ..auth_graph import auth_dataset
from ..auth_models import User
from ..helpers.validate_schema import validate_schema
from ..schemas.users_collection_schemas import create_schema, list_users_schema
from ..helpers.log_helpers import log_event


@before(Secure("Admin"))
class UsersCollectionResource(object):
    """
    summary: Users Collection Resource
    description: Allows administrator to create and list users
    """

    @validate_schema(output_schema=list_users_schema)
    def on_get_v1_0(self, req: Request, resp: Response):
        """
        summary: List users
        externalDocs:
            description: Example of listing users
            url: /docs/api_examples.html#list_users
        responses:
            200:
                description: List of users
                content:
                    application/json:
                        schema: ListUsersSchema
                        examples: UserGetResponseExample
                    application/msgpack:
                        schema: ListUsersSchema
                        examples: UserGetResponseExample
        security:
            - jwt:
                - Admin
        examples:
            - ex_name: UserGetResponseExample
              users:
                - username: admin
                  role: Admin
        """
        users = [
            {"username": u.get_username(), "role": u.role.get_name()}
            for u in User.get_all(auth_dataset)
        ]
        resp.media = {"users": users}
        resp.status = HTTP_200
        log_event(req.context.request_id, "Users info listed")

    @validate_schema(create_schema)
    def on_post_v1_0(self, req: Request, resp: Response):
        """
        summary: Create User
        externalDocs:
            description: Example of creating the user
            url: /docs/api_examples.html#create_user
        requestBody:
            content:
                application/json:
                    schema: CreateUserSchema
                    examples: UserCollectionPostRequestExample
                application/msgpack:
                    schema: CreateUserSchema
                    examples: UserCollectionPostRequestExample
        responses:
            201:
                description: User created
                headers:
                    Location:
                        description: Relative path to the created user
                        schema:
                            type: string
        security:
            - jwt:
                - Admin
        errors:
            - name: AlreadyExistsError
              message: User by username ... already exists!
              target: User
        examples:
            - ex_name: UserCollectionPostRequestExample
              username: carl
              password: Supersecret1111
              role: User
        """
        user = User(auth_dataset).store_user(req.media["username"], req.media["password"], req.media["role"])
        resp.status = HTTP_201
        resp.set_header("Location", "/v1.0/users/" + user.get_username())
        log_event(req.context.request_id, "User added", username=req.media["username"])
