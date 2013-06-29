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
        cls.app = TestApp(app.setup_app())

    
    def test_get_call(self):
        info = {'tempest:1': {'passed': 10}}
        self.api.get_info.return_value = info
        resp = self.app.get('/v1/tempest/1')
        self.api.get_info.assert_called_once_with(
            'tempest', '1')
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), info)

    @patch('ostf_adapter.wsgi.controllers.v1.request')
    def test_post_call(self, request_mock):
        info = {'tempest': 1}
        conf = {'tempest_working_dir': '/opt/stack'}
        request_mock.body = json.dumps(conf)
        self.api.run.return_value = info
        resp = self.app.post_json('/v1/tempest', conf)

        self.api.run.assert_called_once_with('tempest', conf)

        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), info)

    def test_get_call_without_id(self):
        resp = self.app.get('/v1/tempest', expect_errors=True)
        self.assertEqual(resp.status, '400 Bad Request')
        self.assertEqual(json.loads(resp.text),
                         {'message': 'Please provide ID of test run'})

    def test_delete_call_kill_success(self):
        self.api.kill.return_value = True

        resp = self.app.delete('/v1/tempest/1')


        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), 
            {u'message': u'Killed test run with ID 1'})


    def test_delete_call_kill_failure(self):
        self.api.kill.return_value = False

        resp = self.app.delete('/v1/tempest/1')


        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), 
            {u'message': u'Test run 1 already finished'})

    def test_delete_call_without_id(self):
        resp = self.app.delete('/v1/tempest', expect_errors=True)

        self.assertEqual(resp.status, '400 Bad Request')
        self.assertEqual(json.loads(resp.text),
                         {'message': 'Please provide ID of test run'})

    def test_get_all_call(self):
        self.api.commands = {'test': {'test_path': '/some/path'}}
        resp = self.app.get('/v1/')

        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(json.loads(resp.text), 
                        {'test': {'test_path': '/some/path'}})

    def test_head_root_call(self):
        resp = self.app.head('/v1/')

        self.assertEqual(resp.status, '200 OK')

    def test_post_root_call(self):
        resp = self.app.post('/v1/')

        self.assertEqual(resp.status, '200 OK')
        self.assertTrue(resp.text)


    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()