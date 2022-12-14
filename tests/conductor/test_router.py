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

 Tests for VersionedRouter """
import pytest
from unittest.mock import patch
from conductor.src.router import VersionedRouter


class ResourceExample(object):

    def on_get_v1_0(self, req, resp):
        pass

    def on_post_v1_0(self, req, resp):
        pass

    def on_put_v1_0(self, req, resp):
        pass

    def on_patch_v1_0(self, req, resp):
        pass

    def on_delete_v1_0(self, req, resp):
        pass

    def on_head_v1_0(self, req, resp):
        pass

    def on_connect_v1_0(self, req, resp):
        pass

    def on_options_v1_0(self, req, resp):
        pass

    def on_trace_v1_0(self, req, resp):
        pass

    def on_get_v1_1(self, req, resp):
        pass

    def on_post_v1_1(self, req, resp):
        pass

    def on_put_v2_0(self, req, resp):
        pass

    def on_patch_v2_0(self, req, resp):
        pass


@patch("conductor.src.router.config")
def test_add_route_should_add_route_handlers_with_v1_0_suffix(config_mock):
    """ add_route should add routes with sufix v1_0 """
    config = {"versions": [1.0, 1.1, 2.0, 2.2]}
    methods = ["CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"]
    config_mock.__getitem__.side_effect = config.__getitem__
    router = VersionedRouter()
    resource = ResourceExample()
    router.add_route("/example", resource)
    found = router.find("/v1.0/example")
    assert found[0] == resource
    assert all(hasattr(resource, h.__name__) and "v1_0" in h.__name__ for k, h in found[1].items() if k in methods)


@patch("conductor.src.router.config")
def test_add_route_should_add_route_handlers_with_v1_1_suffix(config_mock):
    """ add_route should add routes with sufix v1_1 """
    config = {"versions": [1.0, 1.1, 2.0, 2.2]}
    methods = ["GET", "POST"]
    config_mock.__getitem__.side_effect = config.__getitem__
    router = VersionedRouter()
    resource = ResourceExample()
    router.add_route("/example", resource)
    found = router.find("/v1.1/example")
    assert found[0] == resource
    assert all(hasattr(resource, h.__name__) and "v1_1" in h.__name__ for k, h in found[1].items() if k in methods)


@patch("conductor.src.router.config")
def test_add_route_should_add_route_handlers_with_v2_0_suffix(config_mock):
    """ add_route should add routes with sufix v1_1 """
    config = {"versions": [1.0, 1.1, 2.0]}
    methods = ["PUT", "PATCH"]
    config_mock.__getitem__.side_effect = config.__getitem__
    router = VersionedRouter()
    resource = ResourceExample()
    router.add_route("/example", resource)
    found = router.find("/v2.0/example")
    assert found[0] == resource
    assert all(hasattr(resource, h.__name__) and "v2_0" in h.__name__ for k, h in found[1].items() if k in methods)
