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

 Configure OpenAPI spec generation """
import re
from itertools import count
from apispec import APISpec
from yaml import safe_load
from conductor import api
from conductor.src.router import VersionedRouter
from conductor.src.schemas.datasets_collection_schemas import (
    list_datasets,
    delete_dataset,
    create_dataset
)
from conductor.src.schemas.login_schemas import login_request, login_response
from conductor.src.schemas.roles_collection_schemas import create_schema as roles_create, list_roles_schema
from conductor.src.schemas.tasks_collection_schemas import list_algorithms_schema
from conductor.src.schemas.users_collection_schemas import create_schema as users_create, list_users_schema
from conductor.src.schemas.datasets_schemas import post_input, data_dto, delete_input, error_output
from conductor.src.schemas.files_collection_schemas import files_list
from conductor.src.schemas.operations_schemas import get_response
from conductor.src.schemas.roles_schemas import role_info, role_create
from conductor.src.schemas.tasks_schemas import post_input as task_post, network_construction_input
from conductor.src.schemas.users_schemas import put_schema, patch_schema, get_schema
from conductor.src.schemas.exception import exception_schema
from conductor.src.exceptions import APIError


def flatten_exception_tree(err: APIError):
    """ Get all Exceptions, that implement APIError as a list """
    errors = [err]
    for sub in err.__subclasses__():
        errors.append(sub)
        second = sub.__subclasses__()
        if second:
            for se in second:
                errors = errors + flatten_exception_tree(se)
    return errors


def schema_references(mapping, spec: APISpec):
    """ Set schema names to a reference """
    if isinstance(mapping, dict):
        for k in mapping.keys():
            if k == "schema" and isinstance(mapping[k], str):
                mapping[k] = spec.get_ref("schema", mapping[k])
            else:
                schema_references(mapping[k], spec)


def example_references(mapping: dict, spec: APISpec):
    """ Set example reference """
    if isinstance(mapping, dict):
        for k in mapping.keys():
            if k == "examples":
                if isinstance(mapping[k], list):
                    mapping[k] = {n: spec.get_ref("example", n) for n in mapping[k]}
                else:
                    mapping[k] = {mapping[k]: spec.get_ref("example", mapping[k])}
            else:
                example_references(mapping[k], spec)


def set_errors(mapping: dict, spec: APISpec, exceptions):
    """ Set up errors """
    response_examples = {}
    for err in mapping["errors"]:
        found_error = next(e for e in exceptions if e.code == err["name"])
        error_code = found_error.response_code[:3]
        if error_code not in response_examples:
            response_examples[error_code] = []
        error_example = {
            "summary": err["message"],
            "value": found_error.to_docs_example(err["message"], err["target"], err.get("details"))
        }
        if err["name"] in spec.components.examples:
            for n in count(1, 1):
                temp_name = f"{err['name']}{n}"
                if temp_name not in spec.components.examples:
                    spec.components.example(temp_name, error_example)
                    response_examples[error_code].append(temp_name)
                    break
        else:
            spec.components.example(err["name"], error_example)
            response_examples[error_code].append(err["name"])
    for code in response_examples:
        examples = {n: spec.get_ref("example", n) for n in response_examples[code]}
        mapping["responses"][code] = {
            "description": "Error",
            "content": {
                "application/json": {
                    "schema": spec.get_ref("schema", "APIError"),
                    "examples": examples
                },
                "application/msgpack": {
                    "schema": spec.get_ref("schema", "APIError"),
                    "examples": examples
                }
            }
        }
    del mapping["errors"]
    return mapping


def set_examples(mapping: dict, spec: APISpec):
    """ Set up examples for routes """
    for ex in mapping["examples"]:
        name = ex["ex_name"]
        del ex["ex_name"]
        spec.components.example(name, {"value": ex})
    del mapping["examples"]
    if "requestBody" in mapping:
        example_references(mapping["requestBody"], spec)
    if "responses" in mapping:
        example_references(mapping["responses"], spec)
    return mapping


def spec_path_map(spec: APISpec, router: VersionedRouter, exceptions):
    """ Map documentation path specs to api path mappings """
    for mapping in router._route_mappings:
        mapping_docs = {}
        matcher = f"^on_(?P<method>(get)|(post)|(put)|(patch)|(delete)|(head)|(connect)|(options)|(trace))_{mapping['suffix']}$"
        resource_docs = safe_load(mapping["resource"].__doc__)
        methods = [re.match(matcher, m) for m in dir(mapping["resource"]) if callable(getattr(mapping["resource"], m))]
        methods = [(m.group("method"), getattr(mapping["resource"], m.group(0))) for m in methods if m]
        for m in methods:
            mapping_docs[m[0]] = safe_load(m[1].__doc__)
            if "examples" in mapping_docs[m[0]]:
                mapping_docs[m[0]] = set_examples(mapping_docs[m[0]], spec)
            if "errors" in mapping_docs[m[0]]:
                mapping_docs[m[0]] = set_errors(mapping_docs[m[0]], spec, exceptions)
        schema_references(mapping_docs, spec)
        spec.path(
            mapping["path"],
            operations=mapping_docs,
            summary=resource_docs["summary"],
            description=resource_docs["description"])


jwt_scheme = {
    "description": "JWT token to authenticate user",
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "in": "header",
    "scopes": {
        "User": "Regular user, who can use API functionality",
        "Admin": "Administrator user, who can manage other users"
    }
}

api_info = {
    "description": "API for analyzing networks",
    "version": "1.0",
    "contact": {
        "name": "Maintainer",
        "email": "bozhkov@l3s.de",
        "url": "https://git.l3s.uni-hannover.de/l3s_graph_group/sna"
    }
}

spec = APISpec(
    title="SNA API",
    version="1.0",
    openapi_version="3.0.2",
    info=api_info
)

spec.components.security_scheme("jwt", jwt_scheme)
# DatasetsCollectionResource schemas
spec.components.schema("ListDatasets", list_datasets)
spec.components.schema("DeleteDataset", delete_dataset)
spec.components.schema("CreateDataset", create_dataset)
# DatasetsResource schemas
spec.components.schema("DatasetNodeIds", post_input)
spec.components.schema("DatasetNetwork", data_dto)
spec.components.schema("DatasetErrors", error_output)
spec.components.schema("DatasetDeleteContents", delete_input)
# FilesCollectionResource schemas
spec.components.schema("FileList", files_list)
# LoginResource schemas
spec.components.schema("LoginRequest", login_request)
spec.components.schema("LoginResponse", login_response)
# OperationResource schemas
spec.components.schema("OperationUpdate", get_response)
# RolesCollectionResource schemas
spec.components.schema("RoleRequestSchema", roles_create)
spec.components.schema("RoleListSchema", list_roles_schema)
# TasksResource schemas
spec.components.schema("TaskInput", task_post)
# NetworkConstructionTasksResource schemas
spec.components.schema("NetworkConstructionInput", network_construction_input)
# UsersResource schemas
spec.components.schema("PutUser", put_schema)
spec.components.schema("PatchUser", patch_schema)
spec.components.schema("GetUser", get_schema)
# RolesResource schemas
spec.components.schema("RoleDetails", role_info)
spec.components.schema("CreateRole", role_create)
# TasksCollectionResource schemas
spec.components.schema("ListAlgorithmsSchema", list_algorithms_schema)
# UsersCollectionResource schemas
spec.components.schema("CreateUserSchema", users_create)
spec.components.schema("ListUsersSchema", list_users_schema)
# APIError schema
spec.components.schema("APIError", exception_schema)
# configure exceptions
exceptions = flatten_exception_tree(APIError)

spec_path_map(spec, api._router, exceptions)
