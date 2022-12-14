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

 Schema for network nodes and edges """

network_schema = {
    "oneOf": [
        {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["node"]
                },
                "id": {
                    "type": ["string", "integer"]
                },
                "properties": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"}
                    }
                }
            },
            "required": ["type", "id", "properties"]
        },
        {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["edge"]
                },
                "source": {"type": ["string", "integer"]},
                "target": {"type": ["string", "integer"]},
                "properties": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"}
                    }
                }
            },
            "required": ["type", "source", "target", "properties"]
        }
    ]
}

network_schema_v2 = {
    "type": "object",
    "properties": {
        "directed": {
            "type": "boolean"
        },
        "multigraph": {
            "type": "boolean"
        },
        "graph": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                },
                "version": {
                    "type": "number"
                },
                "id": {
                    "type": "string"
                }
            },
            "required": ["version", "id"]
        },
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    }
                },
                "required": ["id"]
            }
        },
        "links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string"
                    },
                    "target": {
                        "type": "string"
                    }
                },
                "required": ["source", "target"]
            }
        }
    },
    "required": ["directed", "multigraph", "graph", "nodes", "links"]
}
