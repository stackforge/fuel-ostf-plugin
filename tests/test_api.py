import unittest
from mock import patch, MagicMock
from ostf_adapter.api import API, parse_json_file, COMMANDS_FILE_PATH
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
        self.command = TEST_COMMANDS['tests']
        self.storage = MagicMock()

    @patch('ostf_adapter.api.get_storage')
    def test_init_api(self, get_storage_mock):
        get_storage_mock.return_value = 'TEST STORAGE'
        api = API()
        self.assertEqual(api._storage, 'TEST STORAGE')

    @patch('ostf_adapter.api.get_storage')
    @patch('ostf_adapter.api.parse_json_file')
    def test_run(self, commands_mock, get_storage_mock):
        commands_mock.return_value = TEST_COMMANDS
        get_storage_mock.return_value = self.storage
        self.storage.add_test_run.return_value = {'type': TEST_RUN_NAME,
                                                  'id': TEST_RUN_ID}
        api = API()
        with patch.object(api, '_find_command') as find_command_mock:
            find_command_mock.return_value = self.command, self.transport
            res = api.run(TEST_RUN_NAME, CONF)
        self.transport.obj.run.assert_called_once_with(
            TEST_RUN_ID, CONF, driver='nose', test_path='/home/tests')
        self.storage.add_test_run.assert_called_once_with(TEST_RUN_NAME)
        self.assertEqual(res, {'type': TEST_RUN_NAME, 'id': TEST_RUN_ID})

    @patch('ostf_adapter.api.get_storage')
    def test_get_info(self, get_storage_mock):
        get_storage_mock.return_value = self.storage
        api = API()
        res = api.get_info(TEST_RUN_NAME, TEST_RUN_ID)
        self.storage.get_test_results.assert_called_once_with(TEST_RUN_ID)

    @patch('__builtin__.open')
    def test_parse_commands_file(self, file_mock):
        json_example = u"""
            {
                "five_min": {
                    "test_path": "/ostf-tests/fuel/tests",
                    "driver": "nose"
                },
                "fuel_smoke": {
                    "test_path": "/ostf-tests/fuel/tests",
                    "driver": "nose",
                    "argv": ["smoke"]
                },
                "fuel_sanity": {
                    "test_path": "/ostf-tests/fuel/tests",
                    "driver": "nose",
                    "argv": ["sanity"]
                }
            }
        """
        file_mock.return_value = io.StringIO(json_example)
        res = parse_json_file(COMMANDS_FILE_PATH)
        expected = {
            "five_min": {
                "test_path": "/ostf-tests/fuel/tests",
                "driver": "nose"
            },
            "fuel_smoke": {
                "test_path": "/ostf-tests/fuel/tests",
                "driver": "nose",
                "argv": ["smoke"]
            },
            "fuel_sanity": {
                "test_path": "/ostf-tests/fuel/tests",
                "driver": "nose",
                "argv": ["sanity"]
            }
        }
        self.assertEqual(res, expected)

    @patch('ostf_adapter.api.get_storage')
    @patch('ostf_adapter.api.parse_json_file')
    def test_kill_test_run(self, commands_mock, get_storage_mock):
        get_storage_mock.return_value = self.storage
        commands_mock.return_value = TEST_COMMANDS
        self.transport.obj.kill.return_value = True
        api = API()
        with patch.object(api, '_find_command') as find_command_mock:
            find_command_mock.return_value = self.command, self.transport
            res = api.kill(TEST_RUN_NAME, TEST_RUN_ID)
        self.transport.obj.kill.assert_called_once_with(TEST_RUN_ID)
        self.assertTrue(res)

