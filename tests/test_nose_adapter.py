import os
import unittest
from ostf_adapter.transport import nose_adapter
from ostf_adapter.transport import nose_utils
from ostf_adapter.transport import nose_storage_plugin
import io
from mock import patch, MagicMock
from time import time


TEST_RUN_ID = 1
EXTERNAL_ID = 1
CONF = {'keys': 'values'}


patch.TEST_PREFIX = ''


class NoExitStriongIO(io.StringIO):

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestNoseAdapters(unittest.TestCase):

    @patch('ostf_adapter.transport.nose_adapter.storage')
    def setUp(self, storage_mock):
        self.thread = MagicMock()
        self.storage = MagicMock()
        self.module_mock = MagicMock()
        self.config_out = NoExitStriongIO()
        storage_mock.get_storage.return_value = self.storage
        self.driver = nose_adapter.NoseDriver()

    def test_kill(self):
        pass

    @patch('ostf_adapter.transport.nose_adapter.conf')
    @patch('__builtin__.__import__')
    def test_cleanup_call(self, import_mock, conf_mock):
        import_mock.return_value = self.module_mock

        conf_mock.nailgun.host = 'NAILGUN_HOST'
        conf_mock.nailgun.port = 'NAILGUN_PORT'
        self.driver._named_threads[1] = self.thread

        self.driver._clean_up(1, '101', 'cleanup', storage=MagicMock)


class TestNoseUtils(unittest.TestCase):


    def test_config_name_generator_module(self):
        test_path = 'fuel_health.tests'
        external_id = 12
        test_set = 'fuel_health'
        test_path = nose_utils.config_name_generator(
            test_path, test_set, external_id)
        self.assertEqual(test_path.split('/')[-1], 'test_fuel_health_12.conf')

    def test_config_name_generator_relative_path(self):
        test_path = 'functional/dummy_tests/general_test.py'
        external_id = 12
        test_set = 'plugin_general'
        test_path = nose_utils.config_name_generator(
            test_path, test_set, external_id)
        self.assertEqual(test_path.split('/')[-1],
                         'test_plugin_general_12.conf')

    def test_message_matcher(self):
        ex1 = 'Step 2 Failed: Some Message'
        ex2 = 'Step 1 Failed . What is going on'
        self.assertEqual(('2', 'Some Message'), 
            nose_utils.format_failure_message(ex1))
        self.assertEqual(('1', 'What is going on'),
            nose_utils.format_failure_message(ex2))


class TestNoseStoragePlugin(unittest.TestCase):


    @patch('ostf_adapter.transport.nose_storage_plugin.get_storage')
    def setUp(self, get_storage_mock):
        self.storage = MagicMock()
        self.test = MagicMock()
        self.err = MagicMock()
        get_storage_mock.return_value = self.storage
        self.test_parent_id = 12
        self.cluster_id = '14'
        self.plugin = nose_storage_plugin.StoragePlugin(
            self.test_parent_id, self.cluster_id, discovery=False)

    @patch('ostf_adapter.transport.nose_storage_plugin.conf')
    def test_options_interface_defined(self, conf_mock):
        conf_mock.nailgun.host = 'NAILGUN_HOST'
        conf_mock.nailgun.port = 'NAILGUN_PORT'
        self.plugin.options({})

        self.assertEqual(os.environ['CLUSTER_ID'],
                         self.cluster_id)
        self.assertEqual(os.environ['NAILGUN_HOST'],
                         'NAILGUN_HOST')
        self.assertEqual(os.environ['NAILGUN_PORT'],
                         'NAILGUN_PORT')


    def test_add_success_discover_false(self):
        with patch.object(self.plugin, '_add_message') as add_mock:
            self.plugin._start_time = time()
            self.plugin.addSuccess(self.test)
            self.assertEqual(add_mock.call_count, 1)

    def test_add_success_discover_true(self):
        self.plugin.discovery = True
        self.plugin.addSuccess(self.test)
        self.assertEqual(self.storage.add_sets_test.call_count, 1)

    def test_add_failure(self):
        with patch.object(self.plugin, '_add_message') as add_mock:
            self.plugin._start_time = time()
            self.plugin.addFailure(self.test, self.err)
            self.assertEqual(add_mock.call_count, 1)

    def test_add_error(self):
        with patch.object(self.plugin, '_add_message') as add_mock:
            self.plugin._start_time = time()
            self.plugin.addError(self.test, self.err)
            self.assertEqual(add_mock.call_count, 1)

    def test_before_test(self):
        with patch.object(self.plugin, '_add_message') as add_mock:
            self.plugin._start_time = time()
            self.plugin.beforeTest(self.test)
            self.assertEqual(add_mock.call_count, 1)

    def test_describe_test(self):
        self.plugin.describeTest(self.test)