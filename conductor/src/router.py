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

 Custom routing logic, including verioning """
from re import compile
from decimal import Decimal
from falcon.routing import CompiledRouter
from .config import config


class VersionedRouter(CompiledRouter):
    """ Router implementation, that takes into account versioning """

    def __init__(self, *params, **kwargs):
        self._route_mappings = []
        super().__init__(*params, **kwargs)

    matcher = compile(r"^on_((get)|(post)|(put)|(patch)|(delete)|(head)|(connect)|(options)|(trace))_v(?P<major>\d+)_(?P<minor>\d+)$")

    def add_route(self, uri_template, resource, **kwargs):
        """ Add route with version number, using the suffix after the method """
        router = super()
        resource_versions = set()
        config_versions = sorted(config["versions"])
        resource_methods = [m for m in dir(resource) if callable(getattr(resource, m))]
        for m in resource_methods:
            match = self.matcher.match(m)
            if not match:
                continue
            version_major = int(match.group("major"))
            version_minor = int(match.group("minor"))
            resource_versions.add(Decimal(f"{version_major}.{version_minor}"))
        resource_versions = sorted(resource_versions)
        for v in config_versions:
            for rv in resource_versions:
                if rv > v:
                    break
                mv = rv
            mv = mv.as_tuple()
            major_suffix = ''.join(str(n) for n in mv.digits[:mv.exponent])
            minor_suffix = ''.join(str(n) for n in mv.digits[mv.exponent:])
            suffix = f"v{major_suffix}_{minor_suffix}"
            path = f"/v{v}{uri_template}"
            self._route_mappings.append({
                "path": path,
                "resource": resource,
                "suffix": suffix
            })
            router.add_route(path, resource, suffix=suffix)
