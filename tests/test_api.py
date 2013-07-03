import unittest
from mock import patch, MagicMock
from ostf_adapter.api import API, parse_json_file, COMMANDS_FILE_PATH
import io


TEST_RUN_NAME = 'tests'
TEST_RUN_ID = 1
EXTERNAL_ID = 'CLUSTER_ID'
TEST_ID = 'simple.TestSimple'
CONF = {'config': True}
TEST_COMMANDS = {'tests': {
    'driver': 'nose',
    'test_path': '/home/tests'
}}
TEST_RUN = {'id': TEST_RUN_ID, 'external_id': EXTERNAL_ID,
            'type': TEST_RUN_NAME}


class TestApi(unittest.TestCase):

    def setUp(self):
        self.transport = MagicMock()
        self.command = TEST_COMMANDS['tests']
        self.storage = MagicMock()
        self.test_run = MagicMock(**TEST_RUN)

    @patch.object(API, '_discovery')
    @patch('ostf_adapter.api.get_storage')
    def test_init_api(self, get_storage_mock, discovery_mock):
        get_storage_mock.return_value = 'TEST STORAGE'
        api = API()
        discovery_mock.assert_any_call()
        self.assertEqual(api._storage, 'TEST STORAGE')

    @patch.object(API, '_discovery')
    @patch('ostf_adapter.api.get_storage')
    @patch('ostf_adapter.api.parse_json_file')
    def test_run(self, commands_mock, get_storage_mock, discovery_mock):
        commands_mock.return_value = TEST_COMMANDS
        get_storage_mock.return_value = self.storage

        self.transport.obj.check_current_running.return_value = False
        self.storage.add_test_run.return_value = TEST_RUN_ID
        api = API()
        discovery_mock.assert_any_call()
        with patch.object(api, '_find_command') as find_command_mock:
            find_command_mock.return_value = self.command, self.transport
            res = api.run(TEST_RUN_NAME, EXTERNAL_ID, CONF)
        self.transport.obj.run.assert_called_once_with(
            TEST_RUN_ID, EXTERNAL_ID,
            CONF, driver='nose', test_path='/home/tests')
        self.storage.add_test_run.assert_called_once_with(TEST_RUN_NAME,
                                                          EXTERNAL_ID)

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

    @patch.object(API, '_discovery')
    @patch.object(API, '_find_command')
    @patch('ostf_adapter.api.get_storage')
    @patch('ostf_adapter.api.parse_json_file')
    def test_kill_test_run(
            self, commands_mock, get_storage_mock, find_mock, discovery_mock):
        get_storage_mock.return_value = self.storage
        self.transport.check_current_running.return_value = True
        find_mock.return_value = self.command, self.transport
        self.storage.get_last_test_run.return_value = self.test_run
        commands_mock.return_value = TEST_COMMANDS
        self.transport.obj.kill.return_value = True
        api = API()
        with patch.object(api, '_find_command') as find_command_mock:
            find_command_mock.return_value = self.command, self.transport
            res = api.kill(EXTERNAL_ID)
        self.transport.obj.kill.assert_called_once_with(EXTERNAL_ID)

