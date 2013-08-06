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

import multiprocessing
from nose import core
import os
from ostf_adapter import storage
from ostf_adapter.nose_adapter import nose_utils
from ostf_adapter.nose_adapter import nose_storage_plugin
import logging
from pecan import conf


LOG = logging.getLogger(__name__)


class NoseDriver(object):

    def __init__(self):
        LOG.info('NoseDriver initialized')
        self.storage = storage.get_storage()
        self._named_threads = {}

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
        LOG.info('Additional args: %s', argv_add)

        proc = multiprocessing.Process(
            target=self._run_tests,
            args=(test_run_id, external_id, argv_add, command))
        proc.daemon = True
        proc.start()

        self._named_threads[int(test_run_id)] = proc

    def tests_discovery(self, test_set, test_path, argv_add):
        LOG.info('Started test discovery %s', test_set)

        core.TestProgram(
            defaultTest=test_path,
            addplugins=[nose_storage_plugin.StoragePlugin(
                test_set, '', discovery=True)],
            exit=False,
            argv=['tests', '--collect-only'] + argv_add)

    def _run_tests(self, test_run_id, external_id, argv_add, command):
        LOG.info('Nose Driver spawn process for TEST RUN: %s\n'
                     'ARGS: %s' ,test_run_id, argv_add)

        try:
            core.TestProgram(addplugins=[nose_storage_plugin.StoragePlugin(
                test_run_id, str(external_id))],
                exit=False,
                argv=['tests']+argv_add)
            LOG.info('Test run %s finished successfully', test_run_id)
            self.storage.update_test_run(test_run_id, status='finished')
            self._named_threads.pop(int(test_run_id), None)

        except Exception, e:

            LOG.exception('Close process TEST_RUN: %s\n', test_run_id)
            self.storage.update_test_run(test_run_id, status='finished')
            self.storage.update_running_tests(test_run_id,
                                              status='error')

    def kill(self, test_run_id, external_id, cleanup=None):
        LOG.info('Trying to stop process %s', test_run_id)

        if test_run_id in self._named_threads:

            LOG.info('Terminating process: %s', test_run_id)

            self._named_threads[int(test_run_id)].terminate()
            self._named_threads.pop(int(test_run_id), None)

            if cleanup:
                proc = multiprocessing.Process(
                    target=self._clean_up,
                    args=(test_run_id, external_id, cleanup))
                proc.daemon = True
                proc.start()
            else:
                self.storage.update_test_run(test_run_id, status='finished')

            return True
        return False

    def _clean_up(self,
                  test_run_id, external_id, cleanup):
        try:
            module_obj = __import__(cleanup, -1)

            os.environ['NAILGUN_HOST'] = str(conf.nailgun.host)
            os.environ['NAILGUN_PORT'] = str(conf.nailgun.port)
            os.environ['CLUSTER_ID'] = str(external_id)

            module_obj.cleanup.cleanup()

            self.storage.update_test_run(test_run_id, status='finished')
        except Exception:

            LOG.exception('EXCEPTION IN CLEANUP')

            self.storage.update_test_run(test_run_id, status='finished')





