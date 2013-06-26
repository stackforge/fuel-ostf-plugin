import unittest2 as unittest
from core.transport import nose_adapter
import io
from mock import patch, MagicMock
import gevent


TEST_RUN_ID = 1
CONF = {'keys': 'values'}


def raise_system_exit(*args, **kwargs):
    raise SystemExit

def raise_greenlet_exit(*args, **kwargs):
    raise gevent.GreenletExit

class DummyStringIO(io.StringIO):

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@patch('core.transport.nose_adapter.pool')
class TestNoseAdapters(unittest.TestCase):

    def setUp(self):
        self.pool_mock = MagicMock()
        self.thread_mock = MagicMock()


    @patch('core.transport.nose_adapter.io.open')
    def test_prepare_config_conf(self, io_mock, pool_module):
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

    def test_run_with_config_path_with_argv(self, pool_module):
        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        with patch.object(nose_driver, 'prepare_config')\
            as prepare_config_mock:
            res = nose_driver.run(
                TEST_RUN_ID, CONF, config_path='/etc/test.conf', argv='sanity',
                test_path='/home/tests')
        prepare_config_mock.assert_called_once_with(CONF, '/etc/test.conf')
        self.pool_mock.spawn.assert_called_once_with(
            nose_driver._run_tests, TEST_RUN_ID, '/home/tests', ['sanity']
        )
        self.assertIn(1, nose_driver._named_threads)

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

    @patch('core.transport.nose_adapter.main')
    def test_run_tests_raise_system_exit(
            self, nose_test_program_mock, pool_module):
        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        nose_driver._named_threads[TEST_RUN_ID] = 'VALUE'
        nose_test_program_mock.side_effect = raise_system_exit

        self.assertRaises(gevent.GreenletExit, nose_driver._run_tests,
                          TEST_RUN_ID, '/home/tests', ['sanity'])

    @patch('core.transport.nose_adapter.main')
    def test_run_tests_raise_greelet_exit(
            self, nose_test_program_mock, pool_module):
        pool_module.Pool.return_value = self.pool_mock
        nose_driver = nose_adapter.NoseDriver()
        nose_driver._named_threads[TEST_RUN_ID] = 'VALUE'
        nose_test_program_mock.side_effect = raise_greenlet_exit

        self.assertRaises(gevent.GreenletExit, nose_driver._run_tests,
                          TEST_RUN_ID, '/home/tests', ['sanity'])


class TestNoseStoragePlugin(unittest.TestCase):


    def test_storage_plugin_properties(self):
        self.assertEqual(nose_adapter.StoragePlugin.enabled, True)
        self.assertEqual(nose_adapter.StoragePlugin.score, 15000)
        self.assertEqual(nose_adapter.StoragePlugin.name, 'storage')
