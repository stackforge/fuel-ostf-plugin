from core.storage import get_storage
from core.transport import get_transport


class API(object):

    def __init__(self):
        self._storage = get_storage()
        self._transport = get_transport()

    def run(self, service_name):
        service_path = '/home/dshulyak/projects/ceilometer/tests/test_novaclient.py'
        service_id = '{}:{}'.format(service_name, 3)
        self._transport.run(service_path, service_id)
        return {'service_id': service_id}

    def get_info(self, service_id, test_id=None, meta=True):
        if not test_id:
            return self._storage.get_test_results(service_id)
        return self._storage.get_test_result(service_id, test_id, meta=meta)