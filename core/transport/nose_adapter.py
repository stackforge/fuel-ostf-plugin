from nose import main, plugins
import os
from core.storage import get_storage
import gevent
from time import time
import sys
from StringIO import StringIO
from oslo.config import cfg

nose_opts = [
    cfg.StrOpt('default_test_path', default='.',
               help='test path used with nose test runner'),
    cfg.StrOpt('config_template', default='tempest.conf',
               help='template that will be used for running tempest')
]

cfg.CONF.register_opts(nose_opts)


class RedisPlugin(plugins.Plugin):

    enabled = True
    name = 'redis'
    score = 15000

    def __init__(self, test_run_id):

        self._capture = []
        self.test_run_id = test_run_id
        self.storage = get_storage()
        super(RedisPlugin, self).__init__()
        self._current_stderr = None
        self._current_stdout = None
        self._start_capture()

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        self.conf = conf
        self.stats = {'errors': 0,
                      'failures': 0,
                      'passes': 0,
                      'skipped': 0}

    def addSuccess(self, test, capt=None):
        self.stats['passes'] += 1
        self.storage.add_test_result(self.test_run_id, test.id(), {'type': 'success'})

    def addFailure(self, test, err, capt=None, tb_info=None):
        self.stats['failures'] += 1
        self.storage.add_test_result(self.test_run_id, test.id(), {'type': 'failure'})

    def addError(self, test, err, capt=None, tb_info=None):
        self.stats['errors'] += 1
        self.storage.add_test_result(self.test_run_id, test.id(), {'type': 'error'})

    def report(self, stream):
        stats_values = sum(self.stats.values())
        self.stats['total'] = stats_values
        self.storage.add_test_result(self.test_run_id, 'stats', self.stats)

    def _start_capture(self):
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

    def afterTest(self, test):
        self._end_time = time()
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
        return self._start_time - self._end_time


class NoseDriver(object):

    def __init__(self):
        self._default_path = cfg.CONF.default_test_path

    def run(self, test_run):
        gevent.spawn(self._run_tests, test_run, self._default_path)

    def _run_tests(self, service_id, test_path):
        gevent.sleep(0)
        main(defaultTest=None,
             addplugins=[RedisPlugin(service_id)],
             exit=False,
             argv=[service_id] + [test_path])
        raise gevent.GreenletExit



