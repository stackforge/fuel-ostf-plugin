import unittest
from core.transport import nose_adapter, get_transport
from oslo.config import cfg


class TestNoseAdapters(unittest.TestCase):

    def setUp(self):
        setattr(cfg.CONF, 'default_test_path', '.')

    def test_get_nose_transport(self):
        driver = get_transport('tempest')
        self.assertIsInstance(driver, nose_adapter.NoseDriver)

