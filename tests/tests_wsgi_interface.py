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

import unittest2
from mock import patch, MagicMock
from webtest import TestApp
from ostf_adapter.wsgi import app
import json

# patch.TEST_PREFIX = ''

@patch('ostf_adapter.wsgi.controllers.request')
class WsgiInterfaceTests(unittest2.TestCase):

    def setUp(self):
        self.app = TestApp(app.setup_app())

    def test_get_all_tests(self, request):
        self.app.get('/v1/tests')
        request.storage.get_tests.assert_called_once_with()

    def test_get_one_test(self, request):
        self.assertRaises(NotImplementedError,
                          self.app.get,
                          '/v1/tests/1')

    def test_get_all_testsets(self, request):
        self.app.get('/v1/testsets')
        request.storage.get_test_sets.assert_called_once_with()

    def test_get_one_testset(self, request):
        self.assertRaises(NotImplementedError,
                          self.app.get,
                          '/v1/testsets/1')

    def test_get_one_testruns(self, request):
        self.assertRaises(NotImplementedError, self.app.get,
                          '/v1/testruns/1')

    def test_get_all_testruns(self, request):
        self.assertRaises(NotImplementedError, self.app.get,
                          '/v1/testruns')

    def test_post_testruns(self, request):
        testruns = [
            {'testset': 'test_simple',
             'metadata': {'cluster_id': 3}
            },
            {'testset': 'test_simple',
             'metadata': {'cluster_id': 4}
            }]
        request.body = json.dumps(testruns)
        self.app.post_json('/v1/testruns', testruns)

    def test_put_testruns(self, request):
        testruns = [
            {'id': 2,
             'metadata': {'cluster_id': 3},
             'status': 'restarted'
            },
            {'id': 1,
             'metadata': {'cluster_id': 4},
             'status': 'stopped'
            }]
        request.body = json.dumps(testruns)
        request.storage.get_test_run.return_value = MagicMock(frontend={})
        self.app.put_json('/v1/testruns', testruns)

    def test_get_last_testruns(self, request):
        self.app.get('/v1/testruns/last/101')