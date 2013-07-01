import sys
import unittest
from ostf_adapter.transport import nose_adapter
import io
from mock import patch, MagicMock
from time import time
from gevent import GreenletExit


TEST_RUN_ID = 1
CONF = {'keys': 'values'}


@patch('ostf_adapter.transport.nose_adapter.pool')
class TestNoseAdapters(unittest.TestCase):

    def setUp(self):
        self.pool_mock = MagicMock()
        self.thread_mock = MagicMock()
        self.storage_mock = MagicMock()


    @patch('__builtin__.open')
    def test_prepare_config_conf(self, io_mock, pool_module):

        class DummyStringIO(io.StringIO):

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        string_io = DummyStringIO()
        io_mock.return_value = string_io
        conf = {'param1': 'test',
                'param2': 'test'}
        conf_path = '/etc/config.conf'
        res = nose_driver.prepare_config(conf, conf_path)
        self.assertEqual(string_io.getvalue(),
                         u'param2 = test\nparam1 = test\n')

    @patch('ostf_adapter.transport.nose_adapter.get_storage')
    def test_run_with_config_path_with_argv(self, get_storage_mock, pool_module):
        get_storage_mock.return_value = self.storage_mock
        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        with patch.object(nose_driver, 'prepare_config')\
            as prepare_config_mock:
            res = nose_driver.run(
                TEST_RUN_ID, CONF, config_path='/etc/test.conf', argv=['sanity'],
                test_path='/home/tests')
        prepare_config_mock.assert_called_once_with(CONF, '/etc/test.conf')
        self.pool_mock.spawn.assert_called_once_with(
            nose_driver._run_tests, TEST_RUN_ID, '/home/tests', ['sanity'],
            self.storage_mock
        )
        self.assertTrue(1 in nose_driver._named_threads)

    def test_kill_test_run_success(self, pool_module):
        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        nose_driver._named_threads[TEST_RUN_ID] = self.thread_mock

        res = nose_driver.kill(TEST_RUN_ID)
        self.thread_mock.kill.assert_called_once_with()
        self.assertTrue(res)

    def test_kill_test_run_fail(self, pool_module):
        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()

        res = nose_driver.kill(2)
        self.assertFalse(res)

    @patch('ostf_adapter.transport.nose_adapter.main')
    def test_run_tests_raise_system_exit(
            self, nose_test_program_mock, pool_module):
        def raise_system_exit(*args, **kwargs):
            raise SystemExit

        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        nose_driver._named_threads[TEST_RUN_ID] = 'VALUE'
        nose_test_program_mock.side_effect = raise_system_exit

        self.assertRaises(GreenletExit, nose_driver._run_tests,
                          TEST_RUN_ID, '/home/tests', ['sanity'], self.storage_mock)

    @patch('ostf_adapter.transport.nose_adapter.main')
    def test_run_tests_raise_greelet_exit(
            self, nose_test_program_mock, pool_module):

        def raise_greenlet_exit(*args, **kwargs):
            raise GreenletExit

        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        nose_driver._named_threads[TEST_RUN_ID] = 'VALUE'
        nose_test_program_mock.side_effect = raise_greenlet_exit

        self.assertRaises(GreenletExit, nose_driver._run_tests,
                          TEST_RUN_ID, '/home/tests', ['sanity'], self.storage_mock)


class TestNoseStoragePlugin(unittest.TestCase):

    def setUp(self):
        self.storage_mock = MagicMock()

    def test_storage_plugin_properties(self):
        self.assertEqual(nose_adapter.StoragePlugin.enabled, True)
        self.assertEqual(nose_adapter.StoragePlugin.score, 15000)
        self.assertEqual(nose_adapter.StoragePlugin.name, 'storage')

    def test_options_interface_defined(self):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.options([], [])
        self.assertEqual(plugin.test_run_id, TEST_RUN_ID)

    def test_configure_defined(self):
        stats_expected = {'errors': 0,
                          'failures': 0,
                          'passes': 0,
                          'skipped': 0}
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.configure({}, {'conf': 'conf'})
        self.assertEqual(plugin.conf, {'conf': 'conf'})
        self.assertEqual(plugin.stats, stats_expected)

    def test_add_success(self):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.stats = {'passes': 0}
        with patch.object(plugin, '_add_message') as add_message_mock:
            plugin.addSuccess('test')
        add_message_mock.assert_called_once_with('test', type='success')
        self.assertEqual(plugin.stats, {'passes': 1})

    def test_add_failure(self):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.stats = {'failures': 0}
        with patch.object(plugin, '_add_message') as add_message_mock:
            plugin.addFailure('test', 'failure')
        add_message_mock.assert_called_once_with(
            'test', err='failure', type='failure')
        self.assertEqual(plugin.stats, {'failures': 1})

    def test_add_error(self):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.stats = {'errors': 0}
        with patch.object(plugin, '_add_message') as add_message_mock:
            plugin.addError('test', 'error')
        add_message_mock.assert_called_once_with(
            'test', err='error', type='error')
        self.assertEqual(plugin.stats, {'errors': 1})

    def test_report(self):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.stats = {'failures': 1,
                        'passes': 1,
                        'errors': 1}
        stats_expected = {'failures': 1,
                        'passes': 1,
                        'errors': 1,
                        'total': 3}
        plugin.report('stream')
        self.assertEqual(plugin.stats, stats_expected)
        self.storage_mock.update_test_run.assert_called_once_with(
            TEST_RUN_ID, stats_expected)

    @patch('ostf_adapter.transport.nose_adapter.time')
    def test_before_test(self, time_mock):
        test_start_time = time()
        time_mock.return_value = test_start_time
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin.beforeTest('test')
        self.assertEqual(plugin._start_time, test_start_time)

    @patch('ostf_adapter.transport.nose_adapter.sys')
    def test_finalize(self, sys_mock):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin._capture = [('STDOUT', 'STDERR')]
        plugin.finalize('test')
        self.assertEqual(plugin._capture, [])

    @patch('ostf_adapter.transport.nose_adapter.time')
    def test_taken_property(self, time_mock):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        plugin._start_time = time()
        end_time = time()
        time_mock.return_value = end_time
        self.assertEqual(end_time - plugin._start_time, plugin.taken)

    def test_add_message(self):
        plugin = nose_adapter.StoragePlugin(TEST_RUN_ID, self.storage_mock)
        test_mock = MagicMock()
        test_mock.id.return_value = 'test:1'
        plugin._start_time = time()
        plugin._add_message(test_mock, type='test')
        self.assertEqual(self.storage_mock.add_test_result.call_count, 1)
