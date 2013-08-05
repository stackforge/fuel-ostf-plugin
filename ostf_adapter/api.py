#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
from ostf_adapter.storage import get_storage
from ostf_adapter import exceptions as exc
import json
from stevedore import extension
import logging
from pecan import conf


log = logging.getLogger(__name__)


PLUGINS_NAMESPACE = 'plugins'


COMMANDS = {
    "fuel_sanity": {
        "test_path": "fuel_health.tests.sanity",
        "driver": "nose",
        "description": "Sanity tests. Duration 30sec - 2 min",
        "argv": []
    },
    "fuel_smoke": {
        "test_path": "fuel_health.tests.smoke",
        "driver": "nose",
        "description": "Smoke tests. Duration 3 min - 14 min",
        "argv": [],
        "cleanup": "fuel_health.cleanup"
    }
}


def parse_json_file(file_path):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    commands_path = os.path.join(
        current_directory, file_path)
    with open(commands_path, 'r') as f:
        return json.load(f)


class API(object):

    def __init__(self):
        log.info('Initialized API')
        self.commands = {}
        log.info('Parsed commands %s' % self.commands)
        self._storage = get_storage()
        self._transport_manager = extension.ExtensionManager(
            PLUGINS_NAMESPACE, invoke_on_load=True)
        self._discovery()

    def run_multiple(self, test_runs):
        res = []
        for test_run in test_runs:
            test_set = test_run['testset']
            metadata = test_run['metadata']
            tests = test_run.get('tests', [])
            res.append(self.run(test_set, metadata, tests))
        return res

    def run(self, test_set, metadata, tests):
        log.info('Starting test run with metadata %s' % metadata)
        external_id = metadata['cluster_id']
        config = metadata.get('config', {})
        command, transport = self._find_command(test_set)
        data = {}
        if self.check_last_running(test_set, external_id):
            test_run, session = self._storage.add_test_run(
                test_set, external_id, metadata, tests=tests)
            transport.obj.run(
                test_run.id,
                test_run.external_id,
                config,
                command,
                tests,
                test_path=command.get('test_path'),
                argv=command.get('argv', []))
            data = self._prepare_test_run(test_run)
            session.close()
        return data

    def check_last_running(self, test_set, external_id):
        test_run = self._storage.get_last_test_run(test_set, external_id)
        if not test_run:
            return True
        return test_run.status not in ['running']

    def update_multiple(self, test_runs):
        data = []
        for test_run in test_runs:
            status = test_run.get('status')
            if status == 'stopped':
                worker = self.kill(test_run)
            elif status == 'restarted':
                worker = self.restart(test_run)
            data.append(worker)
        return data

    def restart(self, test_run):
        log.info('RESTARTING %s' % test_run)
        status = 'running'
        tests = test_run.get('tests', [])
        test_run = self._storage.get_test_run(test_run['id'])
        if self.check_last_running(test_run.type, test_run.external_id):
            config = json.loads(test_run.data).get('config', {})
            log.info('RESTARTING TEST RUN %s' % test_run)
            command, transport = self._find_command(test_run.type)
            self._storage.update_test_run(test_run.id, status=status)
            if tests:
                self._storage.update_test_run_tests(test_run.id, tests)
            transport.obj.run(test_run.id,
                              test_run.external_id,
                              config,
                              command,
                              tests,
                              test_path=command.get('test_path'),
                              argv=command.get('argv', []))
            return self._prepare_test_run(
                self._storage.get_test_run(test_run.id, joined=True))
        return {}

    def kill(self, test_run):
        status = 'finished'
        test_run = self._storage.get_test_run(test_run['id'])
        log.info('TRYING TO KILL TEST RUN %s' % test_run)
        command, transport = self._find_command(test_run.type)
        cleanup = command.get('cleanup')
        killed = transport.obj.kill(
            test_run.id, test_run.external_id, cleanup=cleanup)
        if killed:
            self._storage.update_running_tests(test_run.id, status='stopped')
        return self._prepare_test_run(
            self._storage.get_test_run(test_run.id, joined=True))

    def get_last_test_run(self, external_id):
        test_runs = self._storage.get_last_test_results(external_id)
        data = []
        for test_run in test_runs:
            data.append(self._prepare_test_run(test_run))
        return data

    def get_test_runs(self):
        test_runs = self._storage.get_test_results()
        response = []
        for test_run in test_runs:
            response.append(self._prepare_test_run(test_run))
        return response

    def get_test_run(self, test_run_id):
        test_run = self._storage.get_test_run(test_run_id, joined=True)
        return self._prepare_test_run(test_run)

    def _prepare_test_run(self, test_run):
        test_run_data = {
            'id': test_run.id,
            'testset': test_run.type,
            'metadata': json.loads(test_run.data),
            'status': test_run.status,
            'started_at': test_run.started_at,
            'ended_at': test_run.ended_at
        }
        tests = []
        if test_run.tests:
            for test in test_run.tests:
                test_data = {'id': test.name,
                             'taken': test.taken,
                             'status': test.status}
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
        self._storage.flush_testsets()
        if conf.debug:
            self.commands = parse_json_file('commands.json')
        else:
            self.commands = COMMANDS
        for test_set in self.commands:
            log.info('PROCESSING %s' % test_set)
            command, transport = self._find_command(test_set)
            argv_add = command.get('argv', [])
            self._storage.add_test_set(test_set, command)
            transport.obj.tests_discovery(test_set, command['test_path'],
                                          argv_add)
        log.info('Finished general test discovery')
        self._storage.update_all_running_test_runs()
        log.info('Finished updating stopped tests')

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