import multiprocessing
from nose import main
from nose.case import Test
from nose.plugins import Plugin
from nose.suite import ContextSuite
import os
from ostf_adapter.storage import get_storage
from time import time
import logging
from ostf_adapter import exceptions as exc


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


class StoragePlugin(Plugin):

    enabled = True
    name = 'storage'
    score = 15000

    def __init__(self, test_parent_id, discovery=False):
        self._capture = []
        self.test_parent_id = test_parent_id
        self.storage = get_storage()
        self.discovery = discovery
        super(StoragePlugin, self).__init__()
        log.info('Storage Plugin initialized')
        self._start_time = None
        self._started = False

    def options(self, parser, env=os.environ):
        pass

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
        log.info('CALLED FOR TEST %s DESC %s' % (test.id(), test.test._testMethodDoc))
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

    def check_current_running(self, unique_id):
        return unique_id in self._named_threads

    def run(self, test_run_id, external_id, conf, **kwargs):
        if 'config_path' in kwargs:
            self.prepare_config(conf, kwargs['config_path'])
        argv_add = kwargs.get('argv', [])
        log.info('Additional args: %s' % argv_add)
        proc = multiprocessing.Process(target=self._run_tests, args=(test_run_id, external_id,
            kwargs['test_path'], argv_add))
        proc.daemon = True
        proc.start()
        self._named_threads[test_run_id] = proc

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

    def _run_tests(self, test_run_id, external_id, test_path, argv_add):
        try:
            log.info('Nose Driver spawn process for TEST RUN: %s\n'
                     'TEST PATH: %s\n'
                     'ARGS: %s' % (test_run_id, test_path, argv_add))
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(test_run_id)],
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
            self.storage.update_running_tests(test_run_id, status='error')
            if test_run_id in self._named_threads:
                del self._named_threads[external_id]

    def kill(self, test_run_id):
        log.info('Trying to stop process %s\n'
                 '%s' % (test_run_id, self._named_threads))
        if test_run_id in self._named_threads:
            log.info('Terminating process: %s' % test_run_id)
            self._named_threads[test_run_id].terminate()
            del self._named_threads[test_run_id]
            return True
        return False

    def prepare_config(self, conf, testing_config_path):

        conf_path = os.path.abspath(testing_config_path)
        with open(conf_path, 'w') as f:
            for key, value in conf.iteritems():
                f.write(u'%s = %s\n' % (key, value))





