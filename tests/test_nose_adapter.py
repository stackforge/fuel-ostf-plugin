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
        driver = get_transport('nose')
        self.assertIsInstance(driver, nose_adapter.NoseDriver)

    @patch('core.transport.nose_adapter.io.open')
    def test_create_tempest_conf(self, io_mock):
        """Test verified
        """
        string_io = DummyStringIO()
        io_mock.return_value = string_io
        conf = {'param1': 'test',
                'param2': 'test'}
        conf_path = '/etc/config.conf'
        res = self.nose_driver.prepare_config(conf, conf_path)
        self.assertEqual(string_io.getvalue(),
                         u'param2 = test\nparam1 = test\n')

