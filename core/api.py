from core.storage import get_storage
from core.transport import get_transport


class API(object):

    def __init__(self):
        self._storage = get_storage()
        self._transport = get_transport()

    def run(self, service_name, conf):
        service_id = self._storage.add_test_run(service_name)
        stored_id = '{}:{}'.format(service_name, service_id)
        self._transport.run(stored_id, conf)
        return {service_name: service_id}

    def get_info(self, service_name, service_id, test_id=None, meta=True):
        stored_id = '{}:{}'.format(service_name, service_id)
        if not test_id:
            return self._storage.get_test_results(stored_id)
        return self._storage.get_test_result(stored_id, test_id, meta=meta)

    def flush_storage(self):
        self._storage.flush_db()