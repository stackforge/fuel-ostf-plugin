import os
from core.storage import get_storage
from core.transport import get_transport
import logging
import yaml

log = logging.getLogger(__name__)


def parse_commands_file():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    commands_path = os.path.join(current_directory, 'commands.yaml')
    with open(commands_path, 'r') as f:
        return yaml.load(f)


class API(object):

    def __init__(self):
        log.info('Initialized API')
        self._commands = parse_commands_file()
        log.info('Parsed commands %s' % self._commands)
        self._storage = get_storage()

    def run(self, test_run_name, conf):
        log.info('Looking for %s in %s' % (test_run_name, self._commands))
        commands_keys = self._commands.get(test_run_name, {})
        transport = get_transport(commands_keys['driver'])
        test_run = self._storage.add_test_run(test_run_name)
        transport.run(test_run['id'], conf, **commands_keys)
        return test_run

    def get_info(self, test_run_name, test_run_id):
        return self._storage.get_test_results(test_run_id)

    def kill(self, test_run_name, test_run_id):
        log.info('Looking for %s in %s' % (test_run_name, self._commands))
        commands_keys = self._commands.get(test_run_name, {})
        transport = get_transport(commands_keys['driver'])
        return transport.kill(test_run_id)
