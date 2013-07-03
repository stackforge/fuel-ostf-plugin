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
        self._discovery()

    def run_multiple(self, test_runs):
        for test_run in test_runs:
            test_set = test_run['testset']
            metadata = test_run['metadata']
            self.run(test_set, metadata)

    def run(self, test_set, metadata):
        log.info('Starting test run with metadata %s' % metadata)
        external_id = metadata['cluster_id']
        config = metadata['config']
        command, transport = self._find_command(test_set)
        if not transport.obj.check_current_running(external_id):
            test_run_id = self._storage.add_test_run(
                test_set, external_id, metadata)
            transport.obj.run(test_run_id, external_id, config, **command)


    def kill_multiple(self, test_runs):
        log.info('Trying to stop tests %s' % test_runs)
        for test_run in test_runs:
            cluster_id = test_run['id']
            status = test_run['status']
            self.kill(cluster_id, status)

    def kill(self, test_run_id, status):
        test_run = self._storage.get_test_run(test_run_id)
        command, transport = self._find_command(test_run.type)
        if transport.obj.check_current_running(test_run.id):
            transport.obj.kill(test_run.id)
            self._storage.update_test_run(test_run_id, status=status)

    def get_last_test_run(self, external_id):
        test_run = self._storage.get_last_test_results(external_id)
        return self._prepare_test_run(test_run)

    def get_test_runs(self):
        test_runs = self._storage.get_test_results()
        response = []
        for test_run in test_runs:
            response.append(self._prepare_test_run(test_run))
        return response

    def _prepare_test_run(self, test_run):
        test_run_data = {
            'id': test_run.id,
            'testset': test_run.type,
            'metadata': json.loads(test_run.data),
            'status': test_run.status
        }
        if test_run.stats:
            test_run_data['stats'] = json.loads(test_run.stats)
        else:
            test_run_data['stats'] = {}
        tests = []
        if test_run.tests:
            for test in test_run.tests:
                test_data = {'id': test.name}
                if test_data:
                    test_data.update(json.loads(test.data))
                tests.append(test_data)
            test_run_data['tests'] = tests
        return test_run_data

    def get_test_sets(self):
        test_sets = self._storage.get_test_sets()
        return [{'id': ts.id, 'name': ts.description} for ts in test_sets]

    def get_tests(self):
        tests = self._storage.get_tests()
        return tests

    def _discovery(self):
        log.info('Started general tests discovery')
        for test_set in self.commands:
            command, transport = self._find_command(test_set)
            argv_add = command.get('argv', [])
            self._storage.add_test_set(test_set, command)
            transport.obj.tests_discovery(test_set, command['test_path'], argv_add)
        log.info('Finished general test discovery')

    def _find_command(self, test_run_name):
        log.info('Looking for %s in %s' % (test_run_name, self.commands))
        command = self.commands.get(test_run_name)
        if not command:
            msg = 'No command for %s in config %s'\
                  % (test_run_name, self.commands)
            log.warning(msg)
            raise exc.OstfNoseException(message=msg)
        try:
            transport = self._transport_manager[command['driver']]
        except KeyError:
            msg = 'No transport for driver %s' % command['driver']
            log.warning(msg)
            raise exc.OstfNoseException(message=msg)
        return command, transport