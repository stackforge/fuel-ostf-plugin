import multiprocessing
from nose import main
from nose.case import Test
from nose.plugins import Plugin
from nose.suite import ContextSuite
import os
from ostf_adapter.storage import get_storage
from time import time
import logging
from ostf_adapter.api import parse_json_file
from ostf_adapter import exceptions as exc
from pecan import conf


TESTS_PROCESS = {}


log = logging.getLogger(__name__)


def get_exc_message(exception_value):
    """
    @exception_value - Exception type object
    """
    _exc_long = str(exception_value)
    if isinstance(_exc_long, basestring):
        return _exc_long.split('\n')[0]
    return u""


def get_description(test_obj):
    if isinstance(test_obj, Test):
        return test_obj.shortDescription()
    else:
        return test_obj.id()


def config_name_generator(test_path, test_set, external_id):
    log.info('CALLED WITH %s' % locals())
    try:
        module_path = os.path.dirname(__import__(test_path).__file__)
        log.info('MODULE PATH IS %s' % module_path)
        return os.path.join(
            module_path,
            'test_{0}_{1}.conf'.format(test_set, external_id))
    except Exception, e:
        log.info('ERROR IN PARSING CONFIG PATH %s' % e)
        current_path = os.path.join(os.path.realpath('.'), test_path)
        dir_path = os.path.dirname(current_path)
        return os.path.join(
            dir_path,
            'test_{0}_{1}.conf'.format(test_set, external_id))


class StoragePlugin(Plugin):

    enabled = True
    name = 'storage'
    score = 15000

    def __init__(
            self, test_parent_id, discovery=False, test_conf_path=''):
        self._capture = []
        self.test_parent_id = test_parent_id
        self.storage = get_storage()
        self.discovery = discovery
        self.test_conf_path = test_conf_path
        super(StoragePlugin, self).__init__()
        log.info('Storage Plugin initialized')
        self._start_time = None
        self._started = False

    def options(self, parser, env=os.environ):
        env['CUSTOM_FUEL_CONFIG'] = self.test_conf_path

    def configure(self, options, conf):
        self.conf = conf

    def _add_message(
            self, test, err=None, capt=None,
            tb_info=None, status=None, taken=0):
        if not self._started:
            self.storage.update_test_run(self.test_parent_id, status='running')
        self._started = True
        data = {}
        data['name'] = get_description(test)
        if err:
            exc_type, exc_value, exc_traceback = err
            log.info('Error %s' % exc_value)
            data['message'] = get_exc_message(exc_value)
        else:
            data['message'] = u''
        if isinstance(test, ContextSuite):
            for sub_test in test._tests:
                data['name'] = get_description(sub_test)
                self.storage.add_test_result(
                    self.test_parent_id, sub_test.id(), status, taken, data)
        else:
            self.storage.add_test_result(
                self.test_parent_id, test.id(), status, taken, data)

    def addSuccess(self, test, capt=None):
        log.info('SUCCESS for %s' % test)
        if self.discovery:
            data = {}
            data['name'] = test.shortDescription()
            data['message'] = u''
            log.info('DISCOVERY FOR %s WITH DATA %s' % (test.id(), data))
            self.storage.add_sets_test(self.test_parent_id, test.id(), data)
        else:
            log.info('UPDATING TEST %s' % test)
            self._add_message(test, status='success', taken=self.taken)

    def addFailure(self, test, err, capt=None, tb_info=None):
        log.info('FAILURE for %s' % test)
        self._add_message(test, err=err, status='failure', taken=self.taken)

    def addError(self, test, err, capt=None, tb_info=None):
        log.info('TEST NAME: %s\n'
                 'ERROR: %s' % (test, err))
        self._add_message(test, err=err, status='error', taken=self.taken)

    def beforeTest(self, test):
        self._start_time = time()
        self._add_message(test, status='running')

    def describeTest(self, test):
        log.info('CALLED FOR TEST %s '
                 'DESC %s' % (test.id(), test.test._testMethodDoc))
        return test.test._testMethodDoc 

    @property
    def taken(self):
        if self._start_time:
            return time() - self._start_time
        return 0


class NoseDriver(object):

    def __init__(self):
        log.info('NoseDriver initialized')
        self.storage = get_storage()
        self._named_threads = {}
        self._configs = parse_json_file('config_templates.json')

    def check_current_running(self, unique_id):
        return unique_id in self._named_threads

    def run(self, test_run_id, external_id,
            conf, test_set, test_path=None, argv=None):
        if conf:
            test_conf_path = self.prepare_config(
                conf, test_path, external_id, test_set)
        else:
            test_conf_path = ''
        argv_add = argv or []
        log.info('Additional args: %s' % argv_add)
        proc = multiprocessing.Process(
            target=self._run_tests,
            args=(test_run_id, external_id, test_path, argv_add, test_conf_path))
        proc.daemon = True
        proc.start()
        self._named_threads[test_run_id] = proc
        log.info('NAMED PROCESS %s' % self._named_threads)

    def tests_discovery(self, test_set, test_path, argv_add):
        try:
            log.info('Started test discovery %s' % test_set)
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(
                     test_set, discovery=True)],
                 exit=False,
                 argv=['tests', '--collect-only']+argv_add)
        except Exception, e:
            log.info('Finished tests discovery %s' % test_set)

    def _run_tests(self, test_run_id, external_id,
                   test_path, argv_add, test_conf_path=''):
        try:
            log.info('Nose Driver spawn process for TEST RUN: %s\n'
                     'TEST PATH: %s\n'
                     'ARGS: %s' % (test_run_id, test_path, argv_add))
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(
                     test_run_id, test_conf_path=test_conf_path)],
                 exit=False,
                 argv=['tests']+argv_add)
            log.info('Test run %s finished successfully' % test_run_id)
            if test_run_id in self._named_threads:
                del self._named_threads[external_id]
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
                del self._named_threads[external_id]

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
                    args=(test_run_id, external_id, test_set, test_path, cleanup))
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

            os.environ['OSTF_CONF_PATH'] = config_name_generator(
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
                with_group = '{}_{}'.format(group_name, group_item)
                if with_group in config:
                    if not template_group:
                        template_group.append('[{0}]'.format(group_name))
                    template_group.append('{0} = {1}'.format(
                        group_item, config[with_group]))
            template.extend(template_group)

        if template:
            conf_path = config_name_generator(test_path, test_set, external_id)
            with open(conf_path, 'w') as f:
                f.write(u'\n'.join(template))
            return conf_path





