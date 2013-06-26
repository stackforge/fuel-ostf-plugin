import unittest
from mock import patch, MagicMock
from core.api import API, parse_commands_file
import io

TEST_RUN_NAME = 'tests'
TEST_RUN_ID = 1
TEST_ID = 'simple.TestSimple'
CONF = {'config': True}
TEST_COMMANDS = {'tests': {
    'driver': 'nose',
    'test_path': '/home/tests'
}}


class TestApi(unittest.TestCase):

    def setUp(self):
        self.transport = MagicMock()
        self.storage = MagicMock()

    @patch('core.api.get_storage')
    def test_init_api(self, get_storage_mock):
        get_storage_mock.return_value = 'TEST STORAGE'
        api = API()
        self.assertEqual(api._storage, 'TEST STORAGE')

    @patch('core.api.get_storage')
    @patch('core.api.parse_commands_file')
    def test_run(self, commands_mock, get_storage_mock):
        commands_mock.return_value = TEST_COMMANDS
        get_storage_mock.return_value = self.storage
        self.storage.add_test_run.return_value = {'type': TEST_RUN_NAME,
                                                  'id': TEST_RUN_ID}
        api = API()
        with patch.object(api, '_transport_manager') as transport_manager_mock:
            transport_manager_mock.__getitem__.side_effect = \
                lambda test_run: self.transport
            res = api.run(TEST_RUN_NAME, CONF)
        self.transport.obj.run.assert_called_once_with(
            TEST_RUN_ID, CONF, driver='nose', test_path='/home/tests')
        self.storage.add_test_run.assert_called_once_with(TEST_RUN_NAME)
        self.assertEqual(res, {'type': TEST_RUN_NAME, 'id': TEST_RUN_ID})

    @patch('core.api.get_storage')
    def test_get_info(self, get_storage_mock):
        get_storage_mock.return_value = self.storage
        api = API()
        res = api.get_info(TEST_RUN_NAME, TEST_RUN_ID)
        self.storage.get_test_results.assert_called_once_with(TEST_RUN_ID)

    @patch('core.api.io.open')
    def test_parse_commands_file(self, file_mock):
        yaml = u"""
            fuel_smoke:
              test_path: /root/ostf-tests/fuel/tests
              driver: nose
              argv: smoke
            fuel_sanity:
              test_path: /root/ostf-tests/fuel/tests
              driver: nose
              argv: sanity
        """
        file_mock.return_value = io.StringIO(yaml)
        res = parse_commands_file()
        expected = {
            'fuel_smoke': {
                'test_path': '/root/ostf-tests/fuel/tests',
                'driver': 'nose',
                'argv': 'smoke'},
            'fuel_sanity': {
                'test_path': '/root/ostf-tests/fuel/tests',
                'driver': 'nose',
                'argv': 'sanity'}
        }
        self.assertEqual(res, expected)

    @patch('core.api.parse_commands_file')
    def test_kill_test_run(self, commands_mock):
        commands_mock.return_value = TEST_COMMANDS
        self.transport.obj.kill.return_value = True
        api = API()
        with patch.object(api, '_transport_manager') as transport_manager_mock:
            transport_manager_mock.__getitem__.side_effect = \
                lambda test_run: self.transport
            res = api.kill(TEST_RUN_NAME, TEST_RUN_ID)
        self.transport.obj.kill.assert_called_once_with(TEST_RUN_ID)
        self.assertTrue(res)

