import unittest
from mock import patch, MagicMock
from ostf_adapter.api import API


TEST_RUN_NAME = 'tests'
TEST_RUN_ID = 1
EXTERNAL_ID = 'CLUSTER_ID'
TEST_ID = 'simple.TestSimple'
CONF = {'config': True}
TEST_COMMANDS = {'fuel_health': {
    'driver': 'nose',
    'test_path': '/home/tests',
}}
TEST_RUN = {'id': TEST_RUN_ID, 'external_id': EXTERNAL_ID,
            'type': TEST_RUN_NAME}


patch.TEST_PREFIX = 'setUp'

class TestApi(unittest.TestCase):

    @patch.object(API, '_discovery')
    @patch('ostf_adapter.api.get_storage')
    @patch('ostf_adapter.api.extension.ExtensionManager')
    def setUp(self, extension_mock, get_storage_mock, discovery_mock):
        self.transport = MagicMock()
        self.command = TEST_COMMANDS['fuel_health']
        self.storage = MagicMock()
        self.test_run = MagicMock(**TEST_RUN)
        self.session = MagicMock()
        get_storage_mock.return_value = self.storage
        self.api = API()
        get_storage_mock.assert_any_call()
        discovery_mock.assert_any_call()

    def test_init_api(self):
        self.assertEqual(self.api._storage, self.storage)

    def test_run_multiple(self):
        test_metadata = [{'testset': 'fuel_health', 'metadata': {}},
            {'testset':'fuel_smoke', 'metadata': {}}]
        with patch.object(self.api, 'run') as run_mock:
            res = self.api.run_multiple(test_metadata)
        self.assertEqual(run_mock.call_count, 2)

    def test_run(self):
        test_set = 'fuel_health'
        metadata = {'cluster_id': 1, 'config': {}}
        tests = ['test_simple']
        with patch.object(self.api, '_prepare_test_run') as prepare_mock:
            with patch.object(self.api, '_find_command') as command_mock:
                command_mock.return_value = (self.command, self.transport)
                self.storage.add_test_run.return_value = (self.test_run,
                                                          self.session)
                self.api.run(test_set, metadata, tests)

    def test_kill_multiple(self):
        test_runs = [{'id': 1, 'status': 'stopped'},
                     {'id': 2, 'status': 'stopped'}]
        with patch.object(self.api, 'kill') as kill_mock:
            self.api.update_multiple(test_runs)
        self.assertEqual(kill_mock.call_count, 2)

    def test_kill(self):
        test_run = {'id': 1}
        status = 'stopped'
        with patch.object(self.api, '_find_command') as command_mock:
            with patch.object(self.api, '_prepare_test_run') as test_run_mock:
                command_mock.return_value = (self.command, self.transport)
                self.api.kill(test_run)
        self.assertEqual(test_run_mock.call_count, 1)