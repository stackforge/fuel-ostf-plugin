from core.storage import redis_storage
import unittest2


class TestRedisStorage(unittest2.TestCase):
    #TODO remove this

    def setUp(self):
        self._r = redis_storage.RedisStorage()

    def test_redis_set(self):
        service_id = 'tempest:2'
        test_id = 'test.test_simple'
        data = {'result': 'TESTED'}
        self._r.add_test_result(service_id, test_id, data)

    def test_redis_get(self):
        service_id = 'tempest:2'
        test_id = 'test.test_simple'
        # res = self._r.get_test_result(service_id, test_id, meta=False)
        # print res

    def test_redis_saving(self):
        service_id = 'ceilometer:3'
        res = self._r.get_test_results(service_id)
        print res

    def test_flush_redis(self):
        # self._r.flush()
        pass