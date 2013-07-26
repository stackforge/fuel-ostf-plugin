#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest
from ostf_adapter.storage.sql_storage import SqlStorage
from ostf_adapter.storage.sql import models
from sqlalchemy import pool


class SqlStorageTests(unittest.TestCase):

    def setUp(self):
        self.test_set_fixtures = {'test_health':
                                      {'description': 'Fixtures of test set'}}
        self.tests_fixtures = [{'name': 'test_simple.TesSimple1',
                                'description': 'SOMETHING WORKS',
                                'message': '',
                                'duration': '',
                                'step': None},
                               {'name': 'test_simple.TesSimple2',
                                'description': 'SOMETHING ELSE WORKS',
                                 'message': '',
                                'duration': '',
                                'step': None}]
        self.storage = SqlStorage('sqlite://', poolclass=pool.QueuePool)
        models.Base.metadata.create_all(self.storage._engine)
        self.storage.add_test_set(*self.test_set_fixtures.items()[0])
        for test in self.tests_fixtures:
            self.storage.add_sets_test('test_health', test['name'], test)
        self.test_run, session = self.storage.add_test_run(
            'test_health', '12', {})

    def test_add_test_run(self):
        external_id = 15
        test_run, session = self.storage.add_test_run(
            'test_health', external_id, {})
        self.assertEqual(test_run.external_id, 15)
        self.assertEqual(len(test_run.tests), 2)

    def test_get_test_sets(self):
        res = self.storage.get_test_sets()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].id, 'test_health')

    def test_get_sets(self):
        res = self.storage.get_tests()
        self.assertEqual(len(res), 2)

    def test_add_sets_test(self):
        test = self.storage.add_sets_test(
            'fuel_health', 'test_simple.TesSimple1',
            {'name': 'SOMETHING HUMAN READABLE'})

    def get_last_test_results(self):
        test_runs = self.storage.get_last_test_results('12')
        self.assertEqual(test_runs[0].id, 1)
        self.assertEqual(len(test_runs[0].tests), 2)
        self.assertEqual(test_runs[0].external_id, '12')

    def test_get_test_run(self):
        test_run = self.storage.get_test_run(self.test_run.id)
        self.assertEqual(test_run.id, self.test_run.id)

    def test_add_test_result(self):
        self.storage.add_test_result(
            self.test_run.id, 'test_simple.TesSimple1',
            'started', 12.0, {'message': 'OK'})

    def test_update_test_run(self):
        self.storage.update_test_run(self.test_run.id, status='finished')

    def test_update_running_tests(self):
        self.storage.update_running_tests(self.test_run.id, status='stopped')

    def test_flush_testsets(self):
        self.storage.flush_testsets()