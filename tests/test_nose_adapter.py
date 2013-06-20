import unittest
from core.transport import nose_adapter, get_transport
from oslo.config import cfg
import io
from mock import patch


class DummyStringIO(io.StringIO):

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestNoseAdapters(unittest.TestCase):

    def setUp(self):
        self.nose_driver = nose_adapter.NoseDriver()

    def test_get_nose_transport(self):
        driver = get_transport('tempest')
        self.assertIsInstance(driver, nose_adapter.NoseDriver)

    @patch.object(nose_adapter, 'CONF')
    def test_parse_test_runs(self, conf_mock):
        conf_mock.test_runs_raw = ['tempest=-A "type == ["sanity", "fuel"]"']
        res = nose_adapter.get_test_run_args('tempest')
        self.assertEqual(res, ['-A "type == ["sanity", "fuel"]"'])

    @patch('core.transport.nose_adapter.io.open')
    @patch.object(nose_adapter, 'CONF')
    def test_create_tempest_conf(self, conf_mock, io_mock):
        conf_mock.overwrite_test_conf = True
        string_io = DummyStringIO()
        io_mock.return_value = string_io
        conf = {'param1': 'test',
                'param2': 'test'}
        res = self.nose_driver.prepare_config(conf)
        self.assertEqual(string_io.getvalue(),
                         u'param2 = test\nparam1 = test\n')

