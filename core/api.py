from core.storage import get_storage
from core.transport import get_transport




class API(object):

    def __init__(self):
        self._storage = get_storage()

    def run(self, test_run_name, conf):
        transport = get_transport(test_run_name)
        test_run_id = self._storage.add_test_run(test_run_name)
        stored_id = '{}:{}'.format(test_run_name, test_run_id)
        transport.run(stored_id, conf)
        return {test_run_name: test_run_id}

    def get_info(self, test_run_name, test_run_id, test_id=None, meta=True):
        stored_id = '{}:{}'.format(test_run_name, test_run_id)
        if not test_id:
            return self._storage.get_test_results(stored_id)
        return self._storage.get_test_result(stored_id, test_id, meta=meta)

    def flush_storage(self):
        self._storage.flush_db()

api = API()