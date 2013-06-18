from nose import main, plugins
import os
from core.storage import get_storage
import gevent
from gevent import pool
from time import time
import sys
from StringIO import StringIO


TESTS_PROCESS = {}


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
        # self._start_capture()

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        self.conf = conf
        self.stats = {'errors': 0,
                      'failures': 0,
                      'passes': 0,
                      'skipped': 0}

    def add_message(self, test, err=None, capt=None, tb_info=None, **kwargs):
        data = {'name': test.id(),
                'taken': self.taken}
        data.update(kwargs)
        self.storage.add_test_result(self.test_run_id, test.id(), data)

    def addSuccess(self, test, capt=None):
        self.stats['passes'] += 1
        self.add_message(test, type='success')

    def addFailure(self, test, err, capt=None, tb_info=None):
        self.stats['failures'] += 1
        self.add_message(test, type='failure')

    def addError(self, test, err, capt=None, tb_info=None):
        self.stats['errors'] += 1
        self.add_message(test, type='error')

    def report(self, stream):
        stats_values = sum(self.stats.values())
        self.stats['total'] = stats_values
        self.storage.add_test_result(self.test_run_id, 'stats', self.stats)
        pass

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
        # self._start_capture()
        pass

    def afterTest(self, test):
        self._end_capture()
        self._current_stdout = None
        self._current_stderr = None

    def startContext(self, context):
        # self._start_capture()
        pass

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

    def run(self, test_run, conf):
        gev = g_pool.spawn(self._run_tests, test_run, [conf['working_directory']])
        TESTS_PROCESS[test_run] = gev

    def _run_tests(self, test_run, argv_add):
        try:
            main(defaultTest=None,
                 addplugins=[StoragePlugin(test_run)],
                 exit=True,
                 argv=['tests']+argv_add)
        finally:
            # del TESTS_PROCESS[test_run]
            raise gevent.GreenletExit

    def kill(self, test_run):
        if test_run in TESTS_PROCESS:
            TESTS_PROCESS[test_run].kill()
            del TESTS_PROCESS[test_run]





