import os
import unittest
from ostf_adapter.transport import nose_adapter
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


    # def test_run_with_config_path_with_argv(
    #         self, get_storage_mock, pool_module):
    #     get_storage_mock.return_value = self.storage_mock
    #     pool_module.Pool.return_value = self.pool_mock
    #     nose_driver = nose_adapter.NoseDriver()
    #     with patch.object(nose_driver, 'prepare_config')\
    #         as prepare_config_mock:
    #         res = nose_driver.run(
    #             TEST_RUN_ID, EXTERNAL_ID, CONF, config_path='/etc/test.conf', argv=['sanity'],
    #             test_path='/home/tests')
    #     prepare_config_mock.assert_called_once_with(CONF, '/etc/test.conf')
    #     self.pool_mock.spawn.assert_called_once_with(
    #         nose_driver._run_tests, TEST_RUN_ID, EXTERNAL_ID, '/home/tests', ['sanity']
    #     )
    #     self.assertTrue(1 in nose_driver._named_threads)
    #
    # def test_kill_test_run_success(self, get_storage_mock, pool_module):
    #     pool_module.Pool.return_value = self.pool_mock
    #     nose_driver = nose_adapter.NoseDriver()
    #     nose_driver._named_threads[TEST_RUN_ID] = self.thread_mock
    #
    #     res = nose_driver.kill(TEST_RUN_ID)
    #     self.thread_mock.kill.assert_called_once_with()
    #     self.assertTrue(res)
    #
    # def test_kill_test_run_fail(self, get_storage_mock, pool_module):
    #     pool_module.Pool.return_value = self.pool_mock
    #     nose_driver = nose_adapter.NoseDriver()
    #
    #     res = nose_driver.kill(2)
    #     self.assertFalse(res)


class TestNoseUtils(unittest.TestCase):


    def test_config_name_generator_module(self):
        test_path = 'fuel_health.tests'
        external_id = 12
        test_set = 'fuel_health'
        test_path = nose_adapter.config_name_generator(
            test_path, test_set, external_id)
        self.assertEqual(test_path.split('/')[-1], 'test_fuel_health_12.conf')

    def test_config_name_generator_relative_path(self):
        test_path = 'functional/dummy_tests/general_test.py'
        external_id = 12
        test_set = 'plugin_general'
        test_path = nose_adapter.config_name_generator(
            test_path, test_set, external_id)
        self.assertEqual(test_path.split('/')[-1],
                         'test_plugin_general_12.conf')

class TestNoseStoragePlugin(unittest.TestCase):

    @patch('ostf_adapter.transport.nose_adapter.get_storage')
    def setUp(self, get_storage_mock):
        self.storage = MagicMock()
        self.test = MagicMock()
        self.err = MagicMock()
        get_storage_mock.return_value = self.storage
        self.test_parent_id = 12
        self.plugin = nose_adapter.StoragePlugin(
            self.test_parent_id, discovery=False,
            test_conf_path='/etc/config.conf')

    def test_options_interface_defined(self):
        self.plugin.options({})

        self.assertEqual(os.environ['CUSTOM_FUEL_CONFIG'],
                         self.plugin.test_conf_path)

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