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

 Dataset resource handler """
from falcon import Request, Response, before, HTTP_200
from ..hooks.secure_resource import Secure
from ..helpers.validate_schema import validate_schema
from ..schemas.datasets_schemas import post_input, data_dto, delete_input, error_output
from ..helpers.network_helpers import split_to_network, network_to_split
from ..helpers.log_helpers import log_event


@before(Secure("User"))
class DatasetsResource(object):
    """
    summary: Dataset Resource
    description: Allows managing the contents of the datasets
    """

    @validate_schema(post_input, data_dto)
    def on_post_v1_0(self, req: Request, resp: Response, dataset_name):
        """
        summary: Get network by node ids
        externalDocs:
            description: Example of getting network by node IDs
            url: /docs/api_examples.html#get_network
        parameters:
            -   in: path
                name: dataset_name
                required: true
                schema:
                    type: string
                description: Dataset ID
        requestBody:
            description: Node IDs
            content:
                application/json:
                    schema: DatasetNodeIds
                    examples: DatasetPostRequestExample
                application/msgpack:
                    schema: DatasetNodeIds
                    examples: DatasetPostRequestExample
        responses:
            200:
                description: Network constructed by found nodes
                content:
                    application/json:
                        schema: DatasetNetwork
                        examples: DatasetPostResponseExample
                    application/msgpack:
                        schema: DatasetNetwork
                        examples: DatasetPostResponseExample
        security:
            - jwt:
                - User
        errors:
            - name: DatasetDoesNotExistError
              message: "Couldn't find dataset by name ..."
              target: dataset name
        examples:
            - ex_name: DatasetPostRequestExample
              nodes:
                - Yayha_al_Azari
            - ex_name: DatasetPostResponseExample
              network:
                - id: Omar_al_Shishani
                  type: node
                  properties:
                    type: group
                    name: Omar al Shishani
                - id: Yayha_al_Azari
                  type: node
                  properties:
                    type: group
                    name: Yayha al Azari
                - source: Omar_al_Shishani
                  target: Yayha_al_Azari
                  type: edge
                  properties:
                    type: friendship
                    observed: true
                    weight: 1
        """
        dataset = req.context.user.get_dataset(dataset_name)
        network = dataset.get_network(req.media["nodes"], req.media.get("params", None))
        resp.media = {
            "network": split_to_network(network["nodes"], network["edges"])
        }
        resp.status = HTTP_200
        log_event(req.context.request_id, "Network returned", dataset=dataset_name)

    @validate_schema(data_dto, error_output)
    def on_patch_v1_0(self, req: Request, resp: Response, dataset_name):
        """
        summary: Update or add nodes
        externalDocs:
            description: Example of updating network
            url: /docs/api_examples.html#update_network
        parameters:
            -   in: path
                name: dataset_name
                required: true
                schema:
                    type: string
                description: Dataset ID
        requestBody:
            description: Network of nodes and edges to be updated
            content:
                application/json:
                    schema: DatasetNetwork
                    examples: DatasetPatchRequestExamle
                application/msgpack:
                    schema: DatasetNetwork
                    examples: DatasetPatchRequestExamle
        responses:
            200:
                description: List of updated nodes and edges that had errors
                content:
                    application/json:
                        schema: DatasetErrors
                        examples: DatasetPatchResponseExample
                    application/msgpack:
                        schema: DatasetErrors
                        examples: DatasetPatchResponseExample
        security:
            - jwt:
                - User
        errors:
            - name: DatasetDoesNotExistError
              message: "Couldn't find dataset by name ..."
              target: dataset name
        examples:
            - ex_name: DatasetPatchRequestExamle
              network:
                - type: node
                  id: Ahmed_Jarrah
                  properties:
                  - type: person
                    name: Ahmed Jarrah
                    attended_Las_Vegas_Meeting: false
                - type: edge
                  source: Majed_Moqed
                  target: Khalid_Al-Mihdhar
                  properties:
                    - type: prior_contact
                      observed: false
                      weight: 0.5
            - ex_name: DatasetPatchResponseExample
              errors: []
        """
        dataset = req.context.user.get_dataset(dataset_name)
        split = network_to_split(req.media["network"])
        node_errors = dataset.save_nodes({n["id"]: n["properties"] for n in split["nodes"]})
        edge_errors = dataset.save_edges(split["edges"])
        resp.media = {
            "errors": node_errors + edge_errors
        }
        resp.status = HTTP_200
        log_event(req.context.request_id, "Nodes and edges updated", dataset=dataset_name)

    @validate_schema(delete_input, error_output)
    def on_delete_v1_0(self, req: Request, resp: Response, dataset_name):
        """
        summary: Remove nodes or edges
        externalDocs:
            description: Example of deleting nodes or edges
            url: /docs/api_examples.html#delete_network
        parameters:
            -   in: path
                name: dataset_name
                required: true
                schema:
                    type: string
                description: Dataset ID
        requestBody:
            description: Lists of nodes and edges to be removed
            content:
                application/json:
                    schema: DatasetDeleteContents
                    examples: DatasetDeleteRequestExample
                application/msgpack:
                    schema: DatasetDeleteContents
                    examples: DatasetDeleteRequestExample
        responses:
            200:
                description: Nodes and edges that had errors during deletion
                content:
                    application/json:
                        schema: DatasetErrors
                        examples: DatasetDeleteResponseExample
                    application/msgpack:
                        schema: DatasetErrors
                        examples: DatasetDeleteResponseExample
        security:
            - jwt:
                - User
        errors:
            - name: DatasetDoesNotExistError
              message: "Couldn't find dataset by name ..."
              target: dataset name
        examples:
            - ex_name: DatasetDeleteRequestExample
              nodes:
                - Ahmed_Jarrah
              edges:
                - source: Yayha_al_Azari
                  target: Sameer_Abd
            - ex_name: DatasetDeleteResponseExample
              errors:
                - success: 0
                  message: node not found!
                  node: Ahmed_Jarrah
        """
        dataset = req.context.user.get_dataset(dataset_name)
        node_errors = []
        edge_errors = []
        if req.media.get("nodes"):
            node_errors = dataset.delete_nodes(req.media["nodes"])
        if req.media.get("edges"):
            edge_errors = dataset.delete_edges([(e["source"], e["target"]) for e in req.media["edges"]], False)
        resp.media = {
            "errors": node_errors + edge_errors
        }
        resp.status = HTTP_200
        log_event(req.context.request_id, "Nodes and edges deleted", dataset=dataset_name)
