from gevent import monkey
monkey.patch_all(thread=False)
import redis


class RedisStorage(object):

    def __init__(self):
        self._r = redis.StrictRedis('localhost')

    def add_test_run(self, service_name):
        return self._r.hincrby('unique', service_name)

    def get_current_test_run(self, service_name):
        return self._r.hget('unique', service_name)

    def get_test_results(self, service_id):
        return {service_id: self._r.hgetall(service_id)}

    def get_test_result(self, service_id, test_id, meta):
        if meta:
            return {service_id: self._r.hmget(service_id, ['meta', test_id])}
        return {service_id: self._r.hget(service_id, test_id)}

    def add_test_result(self, service_id, test_id, data):
        return self._r.hset(service_id, test_id, data)

    def flush_db(self):
        self._r.flushdb()