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

 Role resource """
from falcon import Request, Response, before, HTTP_200, HTTP_201
from ..hooks.secure_resource import Secure
from ..auth_graph import auth_dataset
from ..auth_models import Role, AlreadyExistsError
from ..helpers.validate_schema import validate_schema
from ..exceptions import ValidationError
from ..schemas.roles_schemas import role_info, role_create
from ..helpers.log_helpers import log_event


@before(Secure("Admin"))
class RolesResource(object):
    """
    summary: Roles Resource
    description: Allows managing the roles
    """

    @validate_schema(output_schema=role_info)
    def on_get_v1_0(self, req: Request, resp: Response, role_name):
        """
        summary: Get role info
        externalDocs:
            description: Example of getting role details
            url: /docs/api_examples.html#get_role
        parameters:
            -   in: path
                name: role_name
                required: true
                schema:
                    type: string
                description: Name of the role
        responses:
            200:
                description: Details of the role
                content:
                    application/json:
                        schema: RoleDetails
                    application/msgpack:
                        schema: RoleDetails
        security:
            - jwt:
                - Admin
        errors:
            - name: AuthRecordNotFoundError
              message: "Role not found by name: name"
              target: Role
        examples:
            - ex_name: RoleGetResponseExample
              name: User
              rank: 0
        """
        role = Role(auth_dataset).get_role_vertex(role_name)
        resp.status = HTTP_200
        resp.media = {
            "name": role.get_name(),
            "rank": role.get_rank()
        }
        log_event(
            req.context.request_id,
            "Role info returned",
            role=role_name)

    @validate_schema(input_schema=role_create)
    def on_post_v1_0(self, req: Request, resp: Response, role_name):
        """
        summary: Create new role
        externalDocs:
            description: Example of creating a role by name
            url: /docs/api_examples.html#create_role_name
        parameters:
            -   in: path
                name: role_name
                required: true
                schema:
                    type: string
                description: Name of the role
        requestBody:
            description: New role data
            content:
                application/json:
                    schema: CreateRole
                    examples: RolePostCreateExample
                application/msgpack:
                    schema: CreateRole
                    examples: RolePostCreateExample
        responses:
            201:
                description: Role successfuly created
                headers:
                    Location:
                        description: Relative path to the created role
                        schema:
                            type: string
        security:
            - jwt:
                - Admin
        errors:
            - name: AlreadyExistsError
              message: Role already exists
              target: role name
        examples:
            - ex_name: RolePostCreateExample
              rank: 2
        """
        Role(auth_dataset).add_role(role_name, req.media["rank"])
        resp.set_header("Location", "/v1.0/roles/" + role_name)
        resp.status = HTTP_201
        log_event(
            req.context.request_id,
            "New role created",
            role=role_name)

    @validate_schema(input_schema=role_create)
    def on_patch_v1_0(self, req: Request, resp: Response, role_name):
        """
        summary: Update or create a role
        externalDocs:
            description: Example of updating a role
            url: /docs/api_examples.html#update_role
        parameters:
            -   in: path
                name: role_name
                required: true
                schema:
                    type: string
                description: Name of the role
        requestBody:
            description: Role data
            content:
                application/json:
                    schema: CreateRole
                    examples: RolePatchRequestUpdateExample
                application/msgpack:
                    schema: CreateRole
                    examples: RolePatchRequestUpdateExample
        responses:
            200:
                description: Role updated
            201:
                description: Role successfuly created
                headers:
                    Location:
                        description: Relative path to the created role
                        schema:
                            type: string
        security:
            - jwt:
                - Admin
        errors:
            - name: ValidationError
              message: "To create a role, please provide it's rank"
              target: rank
        examples:
            - ex_name: RolePatchRequestUpdateExample
              rank: 5
        """
        try:
            role = Role(auth_dataset).add_role(role_name, req.media["rank"])
            resp.status = HTTP_201
            resp.set_header("Location", "/v1.0/roles/" + role_name)
            log_event(req.context.request_id, "New role created", role=role_name)
        except AlreadyExistsError:
            role = Role(auth_dataset).get_role_vertex(role_name)
            if req.media.get("rank"):
                role.set_rank(req.media["rank"])
            resp.status = HTTP_200
            log_event(req.context.request_id, "Role edited", role=role_name)
        except KeyError:
            raise ValidationError("To create a role, please provide it's rank", "rank")
