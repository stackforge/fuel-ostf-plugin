from gevent import monkey
monkey.patch_all(thread=False)
import redis

class RedisStorage(object):

    def __init__(self):
        self._r = redis.StrictRedis('localhost')

    def create_test_suite(self, test_suite, job):
        self._r.hset(test_suite, job, {'status': 'INVOKED'})
        return self.get_test_results(test_suite)

    def get_test_results(self, service_id):
        return {service_id: self._r.hgetall(service_id)}

    def get_test_result(self, service_id, test_id, meta):
        if meta:
            res = self._r.hmget(service_id, ['meta', test_id])
        else:
            res = self._r.hget(service_id, test_id)
        return {service_id: res}

    def update_test_results(self, test_suite, job, test_results):
        self._r.hset(test_suite, job, test_results)

    def delete_test_service(self, test_service):
        fields = self._r.hkeys(test_service)
        if fields:
            self._r.hdel(test_service, *fields)

    def get_job_test_results(self, test_service, job):
        return self._r.hget(test_service, job)

    def add_test_result(self, service_id, test_id, data):
        return self._r.hset(service_id, test_id, data)

    def flush(self):
        self._r.flushdb()