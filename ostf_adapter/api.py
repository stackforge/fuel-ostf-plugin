import os
from ostf_adapter.storage import get_storage
from ostf_adapter import exceptions as exc
import simplejson as json
from stevedore import extension
import logging


log = logging.getLogger(__name__)


PLUGINS_NAMESPACE = 'plugins'


COMMANDS_FILE_PATH = 'data/commands.json'


def parse_json_file(file_path):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    commands_path = os.path.join(
        current_directory, os.path.pardir, file_path)
    with open(commands_path, 'r') as f:
        return json.load(f)


class API(object):

    def __init__(self):
        log.info('Initialized API')
        self.commands = parse_json_file(COMMANDS_FILE_PATH)
        log.info('Parsed commands %s' % self.commands)
        self._storage = get_storage()
        self._transport_manager = extension.ExtensionManager(
            PLUGINS_NAMESPACE, invoke_on_load=True)

    def run(self, test_run_name, conf):
        command, transport = self._find_command(test_run_name)
        test_run = self._storage.add_test_run(test_run_name)
        transport.obj.run(test_run['id'], conf, **command)
        return test_run

    def get_info(self, test_run_name, test_run_id):
        return self._storage.get_test_results(test_run_id)

    def kill(self, test_run_name, test_run_id):
        command, transport = self._find_command(test_run_name)
        return transport.obj.kill(test_run_id)

    def _find_command(self, test_run_name):
        log.info('Looking for %s in %s' % (test_run_name, self.commands))
        command = self.commands.get(test_run_name)
        if not command:
            msg = 'No command for %s in config %s'\
                  % (test_run_name, self.commands)
            log.warning(msg)
            raise exc.OstfNoseException(message=msg)
        transport = self._transport_manager.get(command['driver'])
        if not transport:
            msg = 'No transport for driver %s' % command['driver']
            log.warning(msg)
            raise exc.OstfNoseException(message=msg)
        return command, transport