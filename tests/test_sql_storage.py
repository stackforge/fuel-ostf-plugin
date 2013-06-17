import unittest
import mock
from core.storage.sql_storage import SqlStorage
from core.storage.sql import models

class SqlStorageTests(unittest.TestCase):


    def setUp(self):
        self.storage = SqlStorage('sqlite://')
        models.Base.metadata.create_all(self.storage._engine)

    def test_create_session(self):
        res = self.storage.session

    def test_add_test_run(self):
        res = self.storage.add_test_run('test')
        self.assertEqual(res, {'test': 1})

    def tearDown(self):
        with self.storage.session.begin():
            self.storage.session.query(models.Test).delete()
            self.storage.session.query(models.TestRun).delete()
