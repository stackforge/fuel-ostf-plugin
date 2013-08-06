#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from pecan import rest, expose, request
import json


class TestsController(rest.RestController):

    @expose('json')
    def get_one(self):
        return

    @expose('json')
    def get_all(self):
        pass


class TestsetsController(rest.RestController):

    @expose('json')
    def get_one(self, test_set):
        return

    @expose('json')
    def get_all(self):
        pass


class TestrunsController(rest.RestController):

    _custom_actions = {
        'last': ['GET'],
    }

    @expose('json')
    def get_all(self):
        pass

    @expose('json')
    def get_one(self, test_run_id):
        pass

    @expose('json')
    def post(self, body):
        pass

    @expose('json')
    def put(self, body):
        pass

    @expose('json')
    def last(self, cluster_id):
        pass

