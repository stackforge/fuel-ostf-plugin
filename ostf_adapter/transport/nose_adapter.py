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
from ostf_adapter.transport import nose_utils
from ostf_adapter.transport import nose_storage_plugin
import logging
from ostf_adapter import exceptions as exc
from pecan import conf


TESTS_PROCESS = {}


log = logging.getLogger(__name__)


class NoseDriver(object):

    def __init__(self):
        log.info('NoseDriver initialized')
        self.storage = storage.get_storage()
        self._named_threads = {}

    def clean_process(self):
        items = self._named_threads.items()
        for uid, proc in items:
            if not proc.is_alive():
                proc.terminate()
                self._named_threads.pop(uid)

    def check_current_running(self, unique_id):
        return unique_id in self._named_threads

    def run(self, test_run_id, external_id,
            conf, test_set, tests=None, test_path=None, argv=None):
        """
            remove unneceserry arguments
            spawn processes and send them tasks as to workers
        """
        self.clean_process()
        argv_add = argv or []
        tests = tests or []

        if tests:
            log.info('TESTS RECEIVED %s' % tests)
            argv_add += map(nose_utils.modify_test_name_for_nose, tests)
        else:
            argv_add.append(test_path)
        log.info('Additional args: %s' % argv_add)

        proc = multiprocessing.Process(
            target=self._run_tests,
            args=(test_run_id, external_id, argv_add))
        proc.daemon = True
        proc.start()

        self._named_threads[int(test_run_id)] = proc
        log.info('NAMED PROCESS %s' % self._named_threads)

    def tests_discovery(self, test_set, test_path, argv_add):
        log.info('Started test discovery %s' % test_set)

        core.TestProgram(
            defaultTest=test_path,
            addplugins=[nose_storage_plugin.StoragePlugin(
                test_set, '', discovery=True)],
            exit=False,
            argv=['tests', '--collect-only'] + argv_add)

    def _run_tests(self, test_run_id, external_id, argv_add):
        log.info('Nose Driver spawn process for TEST RUN: %s\n'
                     'ARGS: %s' % (test_run_id, argv_add))

        try:
            core.TestProgram(addplugins=[nose_storage_plugin.StoragePlugin(
                test_run_id, str(external_id))],
                exit=False,
                argv=['tests']+argv_add)

            log.info('Test run %s finished successfully' % test_run_id)
            self.storage.update_test_run(test_run_id, status='finished')
            self._named_threads.pop(int(test_run_id), None)

            raise SystemExit

        except Exception, e:

            log.info('Close process TEST_RUN: %s\n'
                     'Thread closed with exception: %s' % (test_run_id,
                                                           e.message))
            self.storage.update_test_run(test_run_id, status='error')
            self.storage.update_running_tests(test_run_id,
                                              status='error')

    def kill(self, test_run_id, external_id, cleanup=None):
        log.info('Trying to stop process %s\n'
                 '%s' % (test_run_id, self._named_threads))
        self.clean_process()

        if test_run_id in self._named_threads:

            log.info('Terminating process: %s' % test_run_id)

            self._named_threads[int(test_run_id)].terminate()
            self._named_threads.pop(int(test_run_id), None)

            if cleanup:
                proc = multiprocessing.Process(
                    target=self._clean_up,
                    args=(test_run_id, external_id, cleanup))
                proc.daemon = True
                proc.start()
                self._named_threads[int(test_run_id)] = proc
            else:
                self.storage.update_test_run(test_run_id, status='stopped')

            return True
        return False

    def _clean_up(self,
                  test_run_id, external_id, cleanup,
                  storage=storage.get_storage):
        #Had problems with mocking storage.get_storage
        storage = storage()
        try:

            log.info("TRYING TO CLEAN")
            module_obj = __import__(cleanup, -1)

            os.environ['NAILGUN_HOST'] = str(conf.nailgun.host)
            os.environ['NAILGUN_PORT'] = str(conf.nailgun.port)
            os.environ['CLUSTER_ID'] = str(external_id)

            log.info('STARTING CLEANUP FUNCTION')
            module_obj.cleanup.cleanup()
            log.info('CLEANUP IS SUCCESSFULL')

            self.storage.update_test_run(test_run_id, status='stopped')
            raise SystemExit
        except Exception, e:

            log.error('EXCITED WITH EXCEPTION %s' % e)
            self.storage.update_test_run(test_run_id, status='error_on_cleanup')




