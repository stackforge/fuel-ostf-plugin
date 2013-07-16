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

    @patch('ostf_adapter.transport.nose_adapter.get_storage')
    def setUp(self, get_storage_mock):
        self.thread = MagicMock()
        self.storage = MagicMock()
        self.config_out = NoExitStriongIO()
        get_storage_mock.return_value = self.storage
        self.driver = nose_adapter.NoseDriver()

    @patch('__builtin__.open')
    def test_prepare_config_conf(self, open_mock):
        open_mock.return_value = self.config_out
        conf = {'network_catalog_type': 'TEST_TYPE',
                'url': 'http://localhost:8989/v1/'}
        test_path = 'fuel_health.tests'
        external_id = 12
        test_set = 'fuel_health'
        self.driver.prepare_config(
            conf, test_path, external_id, test_set)
        self.assertEqual(self.config_out.getvalue(),
                         u'[network]\ncatalog_type = TEST_TYPE\n[identity]\nurl = http://localhost:8989/v1/')


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
            self.test_parent_id, self.cluster_id, discovery=False,
            test_conf_path='/etc/config.conf')

    def test_options_interface_defined(self):
        self.plugin.options({})

        self.assertEqual(os.environ['CUSTOM_FUEL_CONFIG'],
                         self.plugin.test_conf_path)
        self.assertEqual(os.environ['CLUSTER_ID'],
                         self.cluster_id)

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