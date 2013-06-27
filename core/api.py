import os
from core.storage import get_storage
import logging
import simplejson as json
from stevedore import extension
import io

log = logging.getLogger(__name__)


PLUGINS_NAMESPACE = 'plugins'


def parse_commands_file():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    commands_path = os.path.join(
        current_directory, os.path.pardir, 'data/commands.json')
    with io.open(commands_path, 'r') as f:
        return json.load(f)


class API(object):

    def __init__(self):
        log.info('Initialized API')
        self._commands = parse_commands_file()
        log.info('Parsed commands %s' % self._commands)
        self._storage = get_storage()
        self._transport_manager = extension.ExtensionManager(
            PLUGINS_NAMESPACE, invoke_on_load=True)

    def run(self, test_run_name, conf):
        log.info('Looking for %s in %s' % (test_run_name, self._commands))
        command = self._commands.get(test_run_name, {})
        transport = self._transport_manager[command['driver']]
        test_run = self._storage.add_test_run(test_run_name)
        transport.obj.run(test_run['id'], conf, **command)
        return test_run

    def get_info(self, test_run_name, test_run_id):
        return self._storage.get_test_results(test_run_id)

    def kill(self, test_run_name, test_run_id):
        log.info('Looking for %s in %s' % (test_run_name, self._commands))
        command = self._commands.get(test_run_name, {})
        transport = self._transport_manager[command['driver']]
        return transport.obj.kill(test_run_id)
