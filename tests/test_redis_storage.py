from core.storage import redis_storage
import unittest
import json
from nose.tools import nottest


@nottest
class TestRedisStorage(unittest.TestCase):

    def setUp(self):
        self.redis_client = redis_storage.RedisStorage(db=10)
        _raw = self.redis_client._r
        unique_keys_container = 'unique'
        text_run = 'tempest'
        text_run_id = 1
        test_id = 'test_simple.Simple'
        data = json.dumps({'type': 'success'})
        stored_id = '{}:{}'.format(text_run, text_run_id)
        _raw.hincrby(unique_keys_container, text_run)
        _raw.hset(stored_id, test_id, data)
        _raw.hset(stored_id, 'stats', json.dumps({'passed': 1}))

    def test_add_test_run(self):
        test_run = 'tempest'
        expected = 2
        res = self.redis_client.add_test_run(test_run)
        self.assertEqual(res, expected)

    def test_get_current_test_run(self):
        test_run = 'tempest'
        res = self.redis_client.get_current_test_run(test_run)
        self.assertEqual(res, '1')

    def test_get_test_results(self):
        test_run_id = 'tempest:1'
        expected = {test_run_id: {'test_simple.Simple': {'type': 'success'},
                                  'stats': {'passed': 1}}}
        res = self.redis_client.get_test_results(test_run_id)
        self.assertEqual(res, expected)

    def test_get_test_result_without_stats(self):
        test_run_id = 'tempest:1'
        test_id = 'test_simple.Simple'
        expected = {test_run_id: {'test_simple.Simple': {'type': 'success'}}}
        res = self.redis_client.get_test_result(test_run_id, test_id)
        self.assertEqual(res, expected)

    def test_get_test_result_with_stats(self):
        test_run_id = 'tempest:1'
        test_id = 'test_simple.Simple'
        expected = {test_run_id: {'test_simple.Simple': {'type': 'success'},
                                  'stats': {'passed': 1}}}
        res = self.redis_client.get_test_result(test_run_id, test_id, stats=True)
        self.assertEqual(res, expected)

    def test_add_test_result(self):
        test_run_id = 'tempest:1'
        test_id = 'test_simple.SecondSimple'
        data = json.dumps({'type': 'failure'})
        res = self.redis_client.add_test_result(test_run_id, test_id, data)
        self.assertEqual(res, 1)

    def tearDown(self):
        self.redis_client.flush_db()