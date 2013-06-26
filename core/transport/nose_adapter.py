from nose import main, plugins
import os
from core.storage import get_storage
import gevent
from gevent import pool
from time import time
import sys
import logging
import io


TESTS_PROCESS = {}

log = logging.getLogger(__name__)


class StoragePlugin(plugins.Plugin):

    enabled = True
    name = 'storage'
    score = 15000

    def __init__(self, test_run_id):
        self._capture = []
        self.test_run_id = test_run_id
        self.storage = get_storage()
        super(StoragePlugin, self).__init__()
        log.info('Storage Plugin initialized')

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        self.conf = conf
        self.stats = {'errors': 0,
                      'failures': 0,
                      'passes': 0,
                      'skipped': 0}

    def _add_message(self, test, err=None, capt=None, tb_info=None, **kwargs):
        data = {'taken': self.taken}
        data.update(kwargs)
        self.storage.add_test_result(self.test_run_id, test.id(), data)

    def addSuccess(self, test, capt=None):
        log.info('SUCCESS for %s' % test)
        self.stats['passes'] += 1
        self._add_message(test, type='success')

    def addFailure(self, test, err, capt=None, tb_info=None):
        log.info('FAILURE for %s' % test)
        self.stats['failures'] += 1
        self._add_message(test, err=err, type='failure')

    def addError(self, test, err, capt=None, tb_info=None):
        log.info('TEST NAME: %s\n'
                 'ERROR: %s' % (test, err))
        self.stats['errors'] += 1
        self._add_message(test, err=err, type='error')

    def report(self, stream):
        log.info('REPORT')
        stats_values = sum(self.stats.values())
        self.stats['total'] = stats_values
        self.storage.update_test_run(self.test_run_id, self.stats)

    def beforeTest(self, test):
        self._start_time = time()

    def startContext(self, context):
        if not self._capture:
            self._capture.append((sys.stdout, sys.stderr))
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def finalize(self, test):
        while self._capture:
            sys.stdout, sys.stderr = self._capture.pop()

    @property
    def taken(self):
        return time() - self._start_time


class NoseDriver(object):

    def __init__(self):
        log.info('NoseDriver initialized')
        self._pool = pool.Pool(10)
        self._named_threads = {}

    def run(self, test_run_id, conf, **kwargs):
        if 'config_path' in kwargs:
            self.prepare_config(conf, kwargs['config_path'])
        argv_add = []
        if 'argv' in kwargs:
            argv_add = [kwargs['argv']]
        log.info('Additional args: %s' % argv_add)
        gev = self._pool.spawn(
            self._run_tests, test_run_id, kwargs['test_path'], argv_add)
        self._named_threads[test_run_id] = gev

    def _run_tests(self, test_run_id, test_path, argv_add):
        try:
            log.info('Nose Driver spawn green thread for TEST RUN: %s\n'
                     'TEST PATH: %s\n'
                     'ARGS: %s' % (test_run_id, test_path, argv_add))
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(test_run_id)],
                 exit=True,
                 argv=['tests']+argv_add)
        #To close thread we need to catch any exception
        except BaseException, e:
            log.info('Close green thread TEST_RUN: %s\n'
                     'Thread closed with exception: %s' % (test_run_id,
                                                           e.message))
            del self._named_threads[test_run_id]
            raise gevent.GreenletExit

    def kill(self, test_run):
        log.info('Trying to stop process %s\n'
                 '%s' % (test_run, self._named_threads))
        if int(test_run) in self._named_threads:
            log.info('Kill green thread: %s' % test_run)
            self._named_threads[int(test_run)].kill()
            return True
        return False

    def prepare_config(self, conf, testing_config_path):

        conf_path = os.path.abspath(testing_config_path)
        with io.open(conf_path, 'w', encoding='utf-8') as f:
            for key, value in conf.iteritems():
                f.write(u'%s = %s\n' % (key, value))





