import unittest2
from mock import patch
from core.transport import nose_adapter
from oslo.config import cfg


class TestNoseDriver(unittest2.TestCase):

    @patch.object(nose_adapter, 'CONF')
    def test_parse_test_runs(self, conf_mock):
        conf_mock.test_runs_raw = ['tempest=-A type == ["sanity", "fuel"]']
        res = nose_adapter.get_test_run_args('tempest')
        self.assertEqual(res, ['-A type == ["sanity", "fuel"]'])
