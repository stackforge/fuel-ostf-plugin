import unittest
from mock import patch, MagicMock
from core.api import API


TEST_RUN_NAME = 'tempest'
TEST_RUN_ID = 1
TEST_ID = 'simple.TestSimple'
STORED_ID = '{}:{}'.format(TEST_RUN_NAME, TEST_RUN_ID)
CONF = {'config': True}


class TestApi(unittest.TestCase):

    @patch('core.api.get_storage')
    def test_init_api(self, get_storage_mock):
        get_storage_mock.return_value = 'TEST STORAGE'
        api = API()
        self.assertEqual(api._storage, 'TEST STORAGE')

    def setUp(self):
        self.transport = MagicMock()
        self.storage = MagicMock()

    @patch('core.api.get_storage')
    @patch('core.api.get_transport')
    def test_run(self, get_transport_mock, get_storage_mock):
        get_storage_mock.return_value = self.storage
        get_transport_mock.return_value = self.transport
        self.storage.add_test_run.return_value = TEST_RUN_ID
        api = API()
        res = api.run(TEST_RUN_NAME, CONF)
        self.storage.add_test_run.assert_called_once_with(TEST_RUN_NAME)
        self.transport.run.assert_called_once_with(STORED_ID, CONF)
        self.assertEqual(res, {TEST_RUN_NAME: TEST_RUN_ID})

    @patch('core.api.get_storage')
    def test_get_info_without_test_id(self, get_storage_mock):
        get_storage_mock.return_value = self.storage
        api = API()
        res = api.get_info(TEST_RUN_NAME, TEST_RUN_ID)
        self.storage.get_test_results.assert_called_once_with(STORED_ID)

    @patch('core.api.get_storage')
    def test_get_info_with_test_id(self, get_storage_mock):
        get_storage_mock.return_value = self.storage
        api = API()
        res = api.get_info(TEST_RUN_NAME, TEST_RUN_ID, TEST_ID)
        self.storage.get_test_result.assert_called_once_with(
            STORED_ID, TEST_ID, meta=True)
