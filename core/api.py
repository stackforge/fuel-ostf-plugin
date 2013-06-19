from core.storage import get_storage
from core.transport import get_transport
import logging

log = logging.getLogger(__name__)


class API(object):

    def __init__(self):
        log.info('Initialized API')
        self._storage = get_storage()

    def run(self, test_run_name, conf):
        transport = get_transport(test_run_name)
        test_run = self._storage.add_test_run(test_run_name)
        transport.run(test_run['id'], conf)
        return test_run

    def get_info(self, test_run_name, test_run_id):
        return self._storage.get_test_results(test_run_id)

    def kill(self, test_run, test_run_id):
        transport = get_transport(test_run)
        return transport.kill(test_run_id)

api = API()
