import multiprocessing
from nose import main
import os
from ostf_adapter.storage import get_storage
from ostf_adapter.transport import nose_utils
from ostf_adapter.transport import nose_storage_plugin
import logging
from ostf_adapter.api import parse_json_file
from ostf_adapter import exceptions as exc
from pecan import conf


TESTS_PROCESS = {}


log = logging.getLogger(__name__)


class NoseDriver(object):

    def __init__(self):
        log.info('NoseDriver initialized')
        self.storage = get_storage()
        self._named_threads = {}
        self._configs = parse_json_file('config_templates.json')

    def check_current_running(self, unique_id):
        return unique_id in self._named_threads

    def run(self, test_run_id, external_id,
            conf, test_set, tests=None, test_path=None, argv=None):
        if conf:
            test_conf_path = self.prepare_config(
                conf, test_path, external_id, test_set)
        else:
            test_conf_path = ''
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
            args=(test_run_id, external_id, argv_add, test_conf_path))
        proc.daemon = True
        proc.start()
        self._named_threads[test_run_id] = proc
        log.info('NAMED PROCESS %s' % self._named_threads)

    def tests_discovery(self, test_set, test_path, argv_add):
        try:
            log.info('Started test discovery %s' % test_set)
            main(defaultTest=test_path,
                 addplugins=[nose_storage_plugin.StoragePlugin(
                     test_set, '', discovery=True)],
                 exit=False,
                 argv=['tests', '--collect-only'] + argv_add)
        except Exception, e:
            log.info('Finished tests discovery %s' % test_set)

    def _run_tests(self, test_run_id, external_id,
                   argv_add, test_conf_path=''):
        try:
            log.info('Nose Driver spawn process for TEST RUN: %s\n'
                     'ARGS: %s' % (test_run_id, argv_add))
            main(addplugins=[nose_storage_plugin.StoragePlugin(
                test_run_id, str(external_id), test_conf_path=test_conf_path)],
                exit=False,
                argv=['tests']+argv_add)
            log.info('Test run %s finished successfully' % test_run_id)
            if test_run_id in self._named_threads:
                del self._named_threads[test_run_id]
            self.storage.update_test_run(test_run_id, status='finished')
        #To close thread we need to catch any exception
        except Exception, e:
            log.info('Close process TEST_RUN: %s\n'
                     'Thread closed with exception: %s' % (test_run_id,
                                                           e.message))
            self.storage.update_test_run(test_run_id, status='error')
            self.storage.update_running_tests(test_run_id,
                                              status='error')
            if test_run_id in self._named_threads:
                del self._named_threads[test_run_id]

    def kill(self, test_run_id, external_id, test_set,
             test_path=None, cleanup=False):
        log.info('Trying to stop process %s\n'
                 '%s' % (test_run_id, self._named_threads))
        if test_run_id in self._named_threads:
            log.info('Terminating process: %s' % test_run_id)
            self._named_threads[test_run_id].terminate()
            del self._named_threads[test_run_id]
            if cleanup:
                proc = multiprocessing.Process(
                    target=self._clean_up,
                    args=(test_run_id, external_id, test_set,
                          test_path, cleanup))
                proc.daemon = True
                proc.start()
            else:
                self.storage.update_test_run(test_run_id, status='stopped')
            return True
        return False

    def _clean_up(self,
                  test_run_id, external_id, test_set, test_path, cleanup):
        stor = get_storage(conf.dbpath)
        try:
            log.info("TRYING TO CLEAN")
            module_obj = __import__(cleanup, -1)

            os.environ['OSTF_CONF_PATH'] = nose_utils.config_name_generator(
                test_path, test_set, external_id)
            log.info('STARTING CLEANUP FUNCTION')
            module_obj.cleanup.cleanup()
            log.info('CLEANUP IS SUCCESSFULL')
            stor.update_test_run(test_run_id, status='stopped')
        except BaseException, e:
            log.error('EXCITED WITH EXCEPTIOBN %s' % e)
            stor.update_test_run(test_run_id, status='error_on_cleanup')

    def prepare_config(self, config, test_path, external_id, test_set):
        template = []
        for group_name, group_items in self._configs.iteritems():
            template_group = []
            for group_item in group_items:
                if group_item in config:
                    if not template_group:
                        template_group.append('[{0}]'.format(group_name))
                    template_group.append('{0} = {1}'.format(
                        group_item, config[group_item]))
                with_group = '{0}_{1}'.format(group_name, group_item)
                if with_group in config:
                    if not template_group:
                        template_group.append('[{0}]'.format(group_name))
                    template_group.append('{0} = {1}'.format(
                        group_item, config[with_group]))
            template.extend(template_group)

        if template:
            conf_path = nose_utils.config_name_generator(
                test_path, test_set, external_id)
            with open(conf_path, 'w') as f:
                f.write(u'\n'.join(template))
            return conf_path





