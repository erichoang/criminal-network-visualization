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

 Resource to work with specific user """
from falcon import Request, Response, before, HTTP_200, HTTP_201
from ..hooks.secure_resource import Secure
from ..helpers.validate_schema import validate_schema
from ..auth_graph import auth_dataset
from ..auth_models import User, AuthRecordNotFoundError
from ..schemas.users_schemas import put_schema, patch_schema, get_schema
from ..exceptions import ValidationError
from ..helpers.log_helpers import log_event


@before(Secure("Admin"))
class UsersResource(object):
    """
    summary: Users Resource
    description: Allows managing the users
    """

    @validate_schema(output_schema=get_schema)
    def on_get_v1_0(self, req: Request, resp: Response, username):
        """
        summary: Get user details
        externalDocs:
            description: Example of getting user details
            url: /docs/api_examples.html#details_user
        parameters:
            -   in: path
                name: username
                required: true
                schema:
                    type: string
                description: Username
        responses:
            200:
                description: User details
                content:
                    application/json:
                        schema: GetUser
                        examples: UserGetResponseExample
                    application/msgpack:
                        schema: GetUser
                        examples: UserGetResponseExample
        security:
            - jwt:
                - Admin
        errors:
            - name: AuthRecordNotFoundError
              message: User by username ... not found!
              target: username
        examples:
            - ex_name: UserGetListResponseExample
              role:
                name: User
        """
        user = User(auth_dataset).identify(username)
        resp.media = {
            "role": {
                "name": user.role.get_name()
            }
        }
        resp.status = HTTP_200
        log_event(req.context.request_id, "User info returned", username=username)

    @validate_schema(put_schema)
    def on_put_v1_0(self, req: Request, resp: Response, username):
        """
        summary: Replace user or create new
        externalDocs:
            description: Example of replacing user
            url: /docs/api_examples.html#replace_user
        parameters:
            -   in: path
                name: username
                required: true
                schema:
                    type: string
                description: Username
        requestBody:
            description: User data
            content:
                application/json:
                    schema: PutUser
                    examples: UserPutRequestExample
                application/msgpack:
                    schema: PutUser
                    examples: UserPutRequestExample
        responses:
            201:
                description: New user created
                headers:
                    Location:
                        description: Relative path to the new user
                        schema:
                            type: string
            200:
                description: User replaced
        security:
            - jwt:
                - Admin
        examples:
            - ex_name: UserPutRequestExample
              password: Superpass1234
              role: Admin
        """
        try:
            User(auth_dataset).identify(username).delete()
            User(auth_dataset).store_user(username, req.media["password"], req.media["role"])
            resp.status = HTTP_200
            log_event(req.context.request_id, "User replaced", username=username)
        except AuthRecordNotFoundError:
            User(auth_dataset).store_user(username, req.media["password"], req.media["role"])
            resp.set_header("Location", "/v1.0/users/" + username)
            resp.status = HTTP_201
            log_event(req.context.request_id, "User added", username=username)

    @validate_schema(patch_schema)
    def on_patch_v1_0(self, req: Request, resp: Response, username):
        """
        summary: Update user or create new
        externalDocs:
            description: Example of updating user data
            url: /docs/api_examples.html#update_user
        parameters:
            -   in: path
                name: username
                required: true
                schema:
                    type: string
                description: Username
        requestBody:
            description: User data
            content:
                application/json:
                    schema: PatchUser
                    examples: UserPatchRequestExample
                application/msgpack:
                    schema: PatchUser
                    examples: UserPatchRequestExample
        responses:
            201:
                description: New user created
                headers:
                    Location:
                        description: Relative path to the new user
                        schema:
                            type: string
            200:
                description: User updated
        security:
            - jwt:
                - Admin
        examples:
            - ex_name: UserPatchRequestExample
              password: AnotherPass4321
        """
        try:
            user = User(auth_dataset).identify(username)
            if req.media.get("password"):
                user.set_password(req.media["password"])
            if req.media.get("role"):
                user.set_role(req.media["role"])
            resp.status = HTTP_200
            log_event(req.context.request_id, "User updated", username=username)
        except AuthRecordNotFoundError:
            if not req.media.get("password"):
                raise ValidationError("Please provide a password to create a user", "request body")
            if not req.media.get("role"):
                raise ValidationError("Please provide the role name, that user will have", "request body")
            User(auth_dataset).store_user(username, req.media["password"], req.media["role"])
            resp.set_header("Location", "/v1.0/users/" + username)
            resp.status = HTTP_201
            log_event(req.context.request_id, "User added", username=username)

    def on_delete_v1_0(self, req: Request, resp: Response, username):
        """
        summary: Removes a user
        externalDocs:
            description: Example of deleting user
            url: /docs/api_examples.html#remove_user
        parameters:
            -   in: path
                name: username
                required: true
                schema:
                    type: string
                description: Username
        responses:
            200:
                description: User successfuly deleted
        security:
            - jwt:
                - Admin
        errors:
            - name: AuthRecordNotFoundError
              message: User by username ... not found!
              target: username
        """
        User(auth_dataset).identify(username).delete()
        resp.status = HTTP_200
        log_event(req.context.request_id, "User deleted", username=username)
