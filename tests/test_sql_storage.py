import unittest
from ostf_adapter.storage.sql_storage import SqlStorage
from ostf_adapter.storage.sql import models


class SqlStorageTests(unittest.TestCase):

    def setUp(self):
        self.fixture = {'type': 'failure', 'taken': 5,
                         'id': 'fixture.Fixture1'}
        self.stats = {'errors': 0,
                      'failures': 1,
                      'passes': 0,
                      'skipped': 0}
        self.storage = SqlStorage('sqlite://')
        models.Base.metadata.create_all(self.storage._engine)
        self.storage.add_test_run('test')
        self.storage.add_test_result(
            '1', self.fixture['id'], self.fixture)
        self.storage.update_test_run(
            '1', self.stats)

    def test_add_test_run(self):
        res = self.storage.add_test_run('test')
        self.assertEqual(res, {'type': 'test', 'id': 2})

    def test_add_test_result(self):
        data = {'type': 'success', 'taken': 10.5,
                'id': 'test.SimpleTest.test_tests'}
        test = self.storage.add_test_result(
            1, 'test.SimpleTest.test_tests', data)
        self.assertTrue(test.id)

    def test_get_test_results(self):
        test_run_result = self.storage.get_test_results(1)
        expected = {'type': 'test', 'id': 1, 'stats': self.stats,
                    'tests': {self.fixture['id']: self.fixture,
                    }}
        self.assertEqual(test_run_result, expected)

    def test_update_test_run(self):
        res = self.storage.update_test_run(1, {'passes': 1})
        self.assertEqual(res, 1)

