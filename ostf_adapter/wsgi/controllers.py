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

import json

from pecan import rest, expose, request


class BaseRestController(rest.RestController):
    def _handle_get(self, method, remainder):
        if len(remainder):
            method_name = remainder[0]
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    'get_%s' % method_name,
                    method_name
                )
                if controller:
                    return controller, remainder[1:]
        return super(BaseRestController, self)._handle_get(method, remainder)


class TestsController(BaseRestController):

    @expose('json')
    def get_one(self, test_name):
        raise NotImplementedError()

    @expose('json')
    def get_all(self):
        return [item.frontend for item in request.storage.get_tests()]


class TestsetsController(BaseRestController):

    @expose('json')
    def get_one(self, test_set):
        raise NotImplementedError()

    @expose('json')
    def get_all(self):
        return [item.frontend for item in request.storage.get_test_sets()]


class TestrunsController(BaseRestController):

    _custom_actions = {
        'last': ['GET'],
    }

    @expose('json')
    def get_all(self):
        raise NotImplementedError()

    @expose('json')
    def get_one(self, test_run_id):
        raise NotImplementedError()

    @expose('json')
    def get_last(self, cluster_id):
        return [item.frontend for
                item in request.storage.get_last_test_results(cluster_id)]

    @expose('json')
    def post(self):
        test_runs = json.loads(request.body)
        res = []
        for test_run in test_runs:
            test_set = test_run['testset']
            metadata = test_run['metadata']
            tests = test_run.get('tests', [])
            res.append(self._run(test_set, metadata, tests))
        return res

    def _run(self, test_set, metadata, tests):
        test_set = request.storage.get_test_set(test_set)
        transport = request.plugin_manager[test_set.driver]
        if self._check_last_running(test_set.id, metadata['cluster_id']):
            test_run, session = request.storage.add_test_run(
                test_set.id, metadata['cluster_id'], tests=tests)
            transport.obj.run(test_run, test_set)
            data = test_run.frontend
            session.close()
            return data
        return {}

    @expose('json')
    def put(self):
        test_runs = json.loads(request.body)
        data = []
        for test_run in test_runs:
            status = test_run.get('status')
            if status == 'stopped':
                data.append(self._kill(test_run))
            elif status == 'restarted':
                data.append(self._restart(test_run))
        return data

    def _check_last_running(self, test_set, cluster_id):
        test_run = request.storage.get_last_test_run(test_set, cluster_id)
        return not test_run and test_run.is_finished()

    def _restart(self, test_run):
        tests = test_run.get('tests', [])
        test_run = request.storage.get_test_run(test_run['id'])
        if self._check_last_running(test_run.test_set_id, test_run.cluster_id):
            test_set = request.storage.get_test_set(test_run.test_set_id)
            transport = request.plugin_manager[test_set.driver]
            request.storage.update_test_run(test_run.id, status='running')
            if tests:
                request.storage.update_test_run_tests(test_run.id, tests)
            transport.obj.run(test_run, test_set, tests)
            return request.storage.get_test_run(
                test_run.id, joined=True).frontend
        return {}

    def _kill(self, test_run):
        test_run = request.storage.get_test_run(test_run['id'])
        test_set = request.storage.get_test_set(test_run.test_set_id)
        transport = request.plugin_manager[test_set.driver]
        cleanup = test_set.cleanup_path
        killed = transport.obj.kill(
            test_run.id, test_run.cluster_id, cleanup=cleanup)
        if killed:
            request.storage.update_running_tests(test_run.id, status='stopped')
        return request.storage.get_test_run(test_run.id, joined=True).frontend

