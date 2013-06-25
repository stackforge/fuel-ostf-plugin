import unittest
from mock import patch, MagicMock
from core.api import API, parse_commands_file


TEST_RUN_NAME = 'tests'
TEST_RUN_ID = 1
TEST_ID = 'simple.TestSimple'
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
        self.storage.add_test_run.return_value = {'type': TEST_RUN_NAME, 'id':TEST_RUN_ID}
        api = API()
        res = api.run(TEST_RUN_NAME, CONF)
        self.storage.add_test_run.assert_called_once_with(TEST_RUN_NAME)
        self.transport.run.assert_called_once_with(TEST_RUN_ID, CONF)
        self.assertEqual(res, {'type': TEST_RUN_NAME, 'id': TEST_RUN_ID})

    @patch('core.api.get_storage')
    def test_get_info(self, get_storage_mock):
        get_storage_mock.return_value = self.storage
        api = API()
        res = api.get_info(TEST_RUN_NAME, TEST_RUN_ID)
        self.storage.get_test_results.assert_called_once_with(TEST_RUN_ID)

    def test_parse_commands_file(self):
        res = parse_commands_file()
        expected = {'fuel_smoke': {
                    'argv': '-A "type == ["fuel", "smoke"]"',
                      'driver': 'nose',
                      'test_path': '/root/ostf/ostf-tests'},
            'tests': {'driver': 'nose',
                   'test_path': '/home/dshulyak/projects/ostf-tests'}
        }
        self.assertEqual(res, expected)


