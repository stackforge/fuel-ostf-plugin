from core.storage import get_storage
from core.transport import get_transport
from core.wsgi import config as conf
import gevent
import time
from itertools import cycle


JOB_QUEUE = cycle(['tempest_RunServerTests'])


class API(object):

    def __init__(self, conf=conf):
        self._conf = conf
        self._storage = get_storage(conf)
        self._transport = get_transport(conf)

    def invoke_build(self, test_service, job=None):
        if not job:
            job = JOB_QUEUE.next()
        self._transport.invoke_build(job)
        stored_info = self._storage.create_test_suite(test_service, job)
        gevent.spawn(self._handle_update, test_service, job)
        gevent.sleep(0)
        return stored_info

    def _handle_update(self, test_service, job):
        gevent.sleep(0)
        build_status = 'BUILDING'
        while build_status == 'BUILDING':
            build = self._transport.get_last_build(job)
            self._storage.update_test_results(test_service, job, build)
            build_status = build['status']
            time.sleep(3)
        build_result = self._transport.get_last_build_test_result(job)
        build.update(build_result)
        self._storage.update_test_results(test_service, job, build)
        raise gevent.GreenletExit

    def delete_test_service(self, test_service):
        self._storage.delete_test_service(test_service)

    def create_job(self, job_name=None, config=None):
        return True

    def get_test_results(self, test_service):
        return self._storage.get_test_results(test_service)

    def update_test_results(self, test_service, job, test_results):
        return self._storage.update_test_results(test_service, job,
                                                 test_results)