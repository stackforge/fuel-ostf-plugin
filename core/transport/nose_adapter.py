from nose import main, plugins
import os
from core.storage import get_storage
import gevent
from gevent import pool
from time import time
import sys
from StringIO import StringIO
import logging
from oslo.config import cfg
import io



TESTS_PROCESS = {}

log = logging.getLogger(__name__)


class StoragePlugin(plugins.Plugin):

    enabled = True
    name = 'redis'
    score = 15000

    def __init__(self, test_run_id):
        self._capture = []
        self.test_run_id = test_run_id
        self.storage = get_storage()
        super(StoragePlugin, self).__init__()
        self._current_stderr = None
        self._current_stdout = None
        self._start_capture()
        log.info('Storage Plugin initialized')

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        self.conf = conf
        self.stats = {'errors': 0,
                      'failures': 0,
                      'passes': 0,
                      'skipped': 0}

    def add_message(self, test, err=None, capt=None, tb_info=None, **kwargs):
        data = {'taken': self.taken}
        data.update(kwargs)
        self.storage.add_test_result(self.test_run_id, test.id(), data)

    def addSuccess(self, test, capt=None):
        log.info('SUCCESS for %s' % test)
        self.stats['passes'] += 1
        self.add_message(test, type='success')

    def addFailure(self, test, err, capt=None, tb_info=None):
        log.info('FAILURE for %s' % test)
        self.stats['failures'] += 1
        self.add_message(test, type='failure')

    def addError(self, test, err, capt=None, tb_info=None):
        log.info('ERROR for %s\n%s' % (test, err))
        self.stats['errors'] += 1
        self.add_message(test, type='error')

    def report(self, stream):
        log.info('REPORT')
        stats_values = sum(self.stats.values())
        self.stats['total'] = stats_values
        self.storage.add_test_result(self.test_run_id, 'stats', self.stats)

    def _start_capture(self):
        if not self._capture:
            self._capture.append((sys.stdout, sys.stderr))
        self._current_stderr = StringIO()
        self._current_stdout = StringIO()
        sys.stdout = self._current_stdout
        sys.stderr = self._current_stderr

    def _end_capture(self):
        if self._capture:
            sys.stdout, sys.stderr = self._capture.pop()

    def beforeTest(self, test):
        self._start_time = time()
        self._start_capture()
        pass

    def afterTest(self, test):
        self._end_capture()
        self._current_stdout = None
        self._current_stderr = None

    def startContext(self, context):
        self._start_capture()

    def finalize(self, test):
        while self._capture:
            self._end_capture()

    @property
    def captured_stdout(self):
        if self._current_stdout:
            return self._current_stdout.getvalue()
        return ''

    @property
    def captured_stderr(self):
        if self._current_stderr:
            return self._current_stderr.getvalue()
        return ''

    @property
    def taken(self):
        return time() - self._start_time


g_pool = pool.Pool(10)



class NoseDriver(object):

    def run(self, test_run, conf, **kwargs):
        if 'config_path' in kwargs:
            self.prepare_config(conf, kwargs['config_path'])
        argv_add = []
        if 'argv' in kwargs:
            argv_add = [kwargs['argv']]
        log.info('Additional args: %s' % argv_add)
        gev = g_pool.spawn(self._run_tests, test_run, kwargs['test_path'],
                           argv_add)
        TESTS_PROCESS[test_run] = gev

    def _run_tests(self, test_run, test_path, argv_add):
        try:
            log.info('Nose Driver spawn green thread for TEST RUN: %s\n'
                     'TEST PATH: %s\n'
                     'ARGS: %s' % (test_run, test_path, argv_add))
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(test_run)],
                 exit=True,
                 argv=['tests']+argv_add)
        finally:
            log.info('Close green thread TEST_RUN: %s' % test_run)
            del TESTS_PROCESS[test_run]
            raise gevent.GreenletExit

    def kill(self, test_run):
        log.info('Trying to stop process %s\n'
                 '%s' % (test_run, TESTS_PROCESS))
        if int(test_run) in TESTS_PROCESS:
            log.info('Kill green thread: %s' % test_run)
            TESTS_PROCESS[int(test_run)].kill()
            return True
        return False

    def prepare_config(self, conf, testing_config_path):
            conf_path = os.path.abspath(testing_config_path)
            with io.open(conf_path, 'w', encoding='utf-8') as f:
                for key, value in conf.iteritems():
                    f.write(u'%s = %s\n' % (key, value))





