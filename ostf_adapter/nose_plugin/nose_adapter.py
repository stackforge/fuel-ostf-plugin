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
import logging

from nose import core
from pecan import conf

from ostf_adapter import storage
from ostf_adapter.nose_plugin import nose_utils
from ostf_adapter.nose_plugin import nose_storage_plugin


COMMANDS = [
    {
        "id": "fuel_smoke",
        "test_path": "fuel_health.tests.smoke",
        "driver": "nose",
        "description": "Smoke tests. Runs 3 min - 8 min",
        "cleanup_path": "fuel_health.cleanup"
    },
    {
        "id": "fuel_sanity",
        "test_path": "fuel_health.tests.sanity",
        "driver": "nose",
        "description": "Sanity tests. Runs 30sec - 2 min",
    }
]

LOG = logging.getLogger(__name__)


class NoseDriver(object):
    def __init__(self):
        LOG.info('NoseDriver initialized')
        self.storage = storage.get_storage()
        self._named_threads = {}
        self.discovery()

    def discovery(self):
        LOG.info('Started general tests discovery')
        if conf.debug:
            test_sets = nose_utils.parse_json_file('commands.json')
        else:
            test_sets = COMMANDS
        for test_set in test_sets:
            test_set = self.storage.add_test_set(test_set)
            self.tests_discovery(test_set)
        self.storage.update_all_running_test_runs()

    def tests_discovery(self, test_set):
        LOG.info('Started test discovery %s', test_set)

        core.TestProgram(
            defaultTest=test_set.test_path,
            addplugins=[nose_storage_plugin.StoragePlugin(
                test_set.id, '', discovery=True)],
            exit=False,
            argv=['tests_discovery', '--collect-only'])

    def check_current_running(self, unique_id):
        return unique_id in self._named_threads

    def run(self, test_run_id, external_id,
            conf, command, tests=None, test_path=None, argv=None):
        """
            remove unneceserry arguments
            spawn processes and send them tasks as to workers
        """
        argv_add = argv or []
        tests = tests or []

        if tests:
            LOG.info('TESTS RECEIVED %s', tests)
            argv_add += map(nose_utils.modify_test_name_for_nose, tests)
        else:
            argv_add.append(test_path)

        self._named_threads[int(test_run_id)] = nose_utils.run_proc(
            self._run_tests, test_run_id, external_id, argv_add, command)


    def _run_tests(self, test_run_id, external_id, argv_add, command):
        LOG.info('Nose Driver spawn process for TEST RUN: %s\n'
                 'ARGS: %s', test_run_id, argv_add)

        try:
            core.TestProgram(
                addplugins=[nose_storage_plugin.StoragePlugin(
                    test_run_id, str(external_id))],
                exit=False,
                argv=['tests'] + argv_add)
            self._named_threads.pop(int(test_run_id), None)
        except Exception, e:
            LOG.exception('Close process TEST_RUN: %s\n', test_run_id)
        finally:
            self.storage.update_test_run(test_run_id, status='finished')

    def kill(self, test_run_id, external_id, cleanup=None):
        LOG.info('Trying to stop process %s', test_run_id)

        if test_run_id in self._named_threads:

            LOG.info('Terminating process: %s', test_run_id)

            self._named_threads[int(test_run_id)].terminate()
            self._named_threads.pop(int(test_run_id), None)

            if cleanup:
                nose_utils.run_proc(
                    self._clean_up,
                    test_run_id,
                    external_id,
                    cleanup)
            else:
                self.storage.update_test_run(test_run_id, status='finished')

            return True
        return False

    def _clean_up(self, test_run_id, external_id, cleanup):
        try:
            module_obj = __import__(cleanup, -1)

            os.environ['NAILGUN_HOST'] = str(conf.nailgun.host)
            os.environ['NAILGUN_PORT'] = str(conf.nailgun.port)
            os.environ['CLUSTER_ID'] = str(external_id)

            module_obj.cleanup.cleanup()

        except Exception:
            LOG.exception('EXCEPTION IN CLEANUP')

        finally:
            self.storage.update_test_run(test_run_id, status='finished')





