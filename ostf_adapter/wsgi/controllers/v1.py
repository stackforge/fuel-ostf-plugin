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
from ostf_adapter.api import API


class BaseRestController(rest.RestController):

    def _handle_get(self, method, remainder):
        if len(remainder) > 1:
            method_name = '_'.join(remainder[:2])
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    'get_%s' % method_name,
                    method_name
                )
                if controller:
                    return controller, remainder[2:]
        else:
            method_name = remainder[0]
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    'get_%s' % method_name,
                    method_name
                )
                if controller:
                    return controller, []
        return super(BaseRestController, self)._handle_get(method, remainder)


class V1Controller(BaseRestController):
    """
        TODO Rewrite it with wsme expose
    """

    def __init__(self, *args, **kwargs):
        self.api = API()
        super(V1Controller, self).__init__(*args, **kwargs)

    _custom_actions = {
        'testsets': ['GET'],
        'tests': ['GET'],
        'testruns': ['GET', 'POST', 'PUT'],
        'testruns_last': ['GET']
    }

    @expose('json')
    def index(self):
        return {}

    @expose('json')
    def get_testsets(self):
        return self.api.get_test_sets()

    @expose('json')
    def get_tests(self):
        return self.api.get_tests()

    @expose('json')
    def get_testruns(self, id=None):
        if not id:
            return self.api.get_test_runs()
        return self.api.get_test_run(id)

    @expose('json')
    def get_testruns_last(self, external_id):
        return self.api.get_last_test_run(external_id)

    @expose('json')
    def post_testruns(self):
        test_runs = json.loads(request.body)
        return self.api.run_multiple(test_runs)

    @expose('json')
    def put_testruns(self):
        test_runs = json.loads(request.body)
        return self.api.update_multiple(test_runs)
