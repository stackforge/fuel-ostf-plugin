from gevent import monkey
monkey.patch_all(thread=False)
import redis
import json


class RedisStorage(object):

    def __init__(self):
        self._r = redis.StrictRedis('localhost')

    def add_test_run(self, test_run):
        return self._r.hincrby('unique', test_run)

    def get_current_test_run(self, test_run):
        return self._r.hget('unique', test_run)

    def get_test_results(self, test_run_id):
        res = self._r.hgetall(test_run_id)
        res = {key: json.loads(value) for key, value in res.iteritems()}
        return {test_run_id: res}

    def get_test_result(self, test_run_id, test_id, stats=False):
        res = {}
        if stats:
            res.update({'stats': json.loads(self._r.hget(test_run_id, 'stats'))})
        res.update({test_id: json.loads(self._r.hget(test_run_id, test_id))})
        return {test_run_id: res}

    def add_test_result(self, test_run_id, test_id, data):
        return self._r.hset(test_run_id, test_id, data)

    def flush_db(self):
        self._r.flushdb()