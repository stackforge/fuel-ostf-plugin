import unittest
from mock import patch, MagicMock
from webtest import TestApp
from ostf_adapter.wsgi import app
import simplejson as json


class ApiV1Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.patcher = patch('ostf_adapter.wsgi.controllers.v1.API')
        cls.api = MagicMock(name='api_instance')
        api_mock = cls.patcher.start()
        api_mock.return_value = cls.api
        app.setup_config(app.pecan_config_dict)
        cls.app = TestApp(app.setup_app())

    def test_get_tests_call(self):
        expected = [
            {'id': "testset-nova-1", 'name': "Tests for nova"},
            {'id': "testset-keystone-222", 'name': "Tests for keystone"},
        ]
        self.api.get_test_sets.return_value = expected
        resp = self.app.get('/v1/testsets')
        self.api.get_test_sets.assert_any_call()
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), expected)

    def test_get_tests(self):
        expected = [
            {'id': "test_for_adapter.TestSimple.test_first_without_sleep_1",
             'name': "Some test #1", 'testset': "testset-nova-1"},
            {'id': "test_for_adapter.TestSimple.test_first_without_sleep_2",
             'name': "Some test #2", 'testset': "testset-nova-1"},
            {'id': "test_for_keystone.TestSimple.fgsfds",
             'name': "Another test", 'testset': "testset-keystone-222"},
        ]
        self.api.get_tests.return_value = expected
        resp = self.app.get('/v1/tests')
        self.api.get_tests.assert_any_call()
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), expected)

    def test_get_test_runs(self):
        """Simply get all test runs
        """
        expected = [
             {'id': '1', 'testset': "testset-keystone-222", 'metadata':
                 {'stats':
                      {'error': '1', 'failure': '0',
                       'success': '0', 'total': '1'}},
              'tests': [
              {'id': "test_for_adapter.TestSimple.test_first_without_sleep_1",
               'status': "error", 'message': "error message if error"},
                ]
            },
        ]
        self.api.get_test_runs.return_value = expected
        resp = self.app.get('/v1/testruns')
        self.api.get_test_runs.assert_any_call()
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), expected)

    def test_get_last_test_runs(self):
        expected = \
        {'id': '1', 'testset': "testset-keystone-222", 'metadata':
            {'stats':
                {'error': '1', 'failure': '0',
                'success': '0', 'total': '1'}},
        'tests': [
            {'id': "test_for_adapter.TestSimple.test_first_without_sleep_1",
            'status': "error", 'message': "error message if error"},
            ]
        }
        self.api.get_last_test_run.return_value = expected
        resp = self.app.get('/v1/testruns/last/1')
        self.api.get_last_test_run.assert_called_once_with('1')
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), expected)

    def test_get_test_run(self):
        expected = \
        {'id': '1', 'testset': "testset-keystone-222", 'metadata':
            {'stats':
                {'error': '1', 'failure': '0',
                'success': '0', 'total': '1'}},
        'tests': [
            {'id': "test_for_adapter.TestSimple.test_first_without_sleep_1",
            'status': "error", 'message': "error message if error"},
            ]
        }
        self.api.get_test_run.return_value = expected
        resp = self.app.get('/v1/testruns?id=1')
        self.api.get_test_run.assert_called_once_with('1')
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), expected)

    def test_post_test_runs(self):
        body = [
             {'testset': "fuel_sanity",
            'metadata': {'cluster_id': '1',
                         'config': {'property': 'value'}}},
            ]
        resp = self.app.post_json('/v1/testruns', body)
        self.api.run_multiple.assert_called_once_with(body)
        self.assertEqual(resp.status, '200 OK')

    def test_put_test_runs(self):
        body = [
            {'id': 'HHH', 'status': "stopped"},
        ]
        resp = self.app.put_json('/v1/testruns', body)
        self.api.kill_multiple.assert_called_once_with(body)
        self.assertEqual(resp.status, '200 OK')

    def test_index_v1(self):
        resp = self.app.get('/v1/')
        self.assertEqual(resp.status, '200 OK')

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()