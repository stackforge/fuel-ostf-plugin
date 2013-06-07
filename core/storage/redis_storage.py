import redis
from gevent import monkey

monkey.patch_all()


class RedisStorage(object):

    def __init__(self):
        self._r = redis.StrictRedis('localhost')

    def create_test_suite(self, test_suite, job):
        self._r.hset(test_suite, job, {'status': 'INVOKED'})
        return self.get_test_results(test_suite)

    def get_test_results(self, test_suite):
        return {test_suite: self._r.hgetall(test_suite)}

    def update_test_results(self, test_suite, job, test_results):
        self._r.hset(test_suite, job, test_results)

    def delete_test_service(self, test_service):
        fields = self._r.hkeys(test_service)
        if fields:
            self._r.hdel(test_service, *fields)

    def get_job_test_results(self, test_service, job):
        return self._r.hget(test_service, job)