import unittest2
from mock import patch
from webtest import TestApp
from core.wsgi import app
import simplejson as json


class ApiV1Tests(unittest2.TestCase):

    def setUp(self):
        self.app = TestApp(app.setup_app())

    @patch('core.wsgi.controllers.v1.request')
    def test_get_call(self, request_mock):
        info = {'tempest:1': {'passed': 10}}
        request_mock.api.get_info.return_value = info
        resp = self.app.get('/v1/tempest?test_run_id=1')

        request_mock.api.get_info.assert_called_once_with(
            'tempest', '1')

        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), info)

    @patch('core.wsgi.controllers.v1.request')
    def test_post_call(self, request_mock):
        info = {'tempest': 1}
        conf = {'tempest_working_dir': '/opt/stack'}
        request_mock.body = json.dumps(conf)
        request_mock.api.run.return_value = info
        resp = self.app.post_json('/v1/tempest', conf)

        request_mock.api.run.assert_called_once_with('tempest', conf)

        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), info)

    def test_post_call_without_conf(self):
        resp = self.app.post('/v1/tempest', expect_errors=True)
        self.assertEqual(resp.status, '400 Bad Request')
        self.assertEqual(json.loads(resp.text),
                         {'message': 'Config is expected'})

    def test_get_call_without_id(self):
        resp = self.app.get('/v1/tempest', expect_errors=True)
        self.assertEqual(resp.status, '400 Bad Request')
        self.assertEqual(json.loads(resp.text),
                         {'message': 'Please provide ID of test run'})

