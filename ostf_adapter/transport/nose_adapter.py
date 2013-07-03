from nose import main
from nose.plugins import Plugin
import os
from ostf_adapter.storage import get_storage
import gevent
from gevent import pool
from time import time
import logging
import traceback
from ostf_adapter import exceptions as exc


TESTS_PROCESS = {}

log = logging.getLogger(__name__)


class StoragePlugin(Plugin):

    enabled = True
    name = 'storage'
    score = 15000

    def __init__(self, test_run_id, storage, discovery=False):
        self._capture = []
        self.test_run_id = test_run_id
        self.storage = storage
        self.discovery = discovery
        super(StoragePlugin, self).__init__()
        log.info('Storage Plugin initialized')
        self._start_time = None

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        self.conf = conf
        self.stats = {'errors': 0,
                      'failures': 0,
                      'passes': 0,
                      'skipped': 0}

    def _add_message(self, test, err=None, capt=None, tb_info=None, **kwargs):
        data = dict()
        data['message'] = u""
        data['traceback'] = u""
        if err:
            exc_type, exc_value, exc_traceback = err
            log.info('Error %s' % exc_value)
            if hasattr(exc_value, 'message'):
                data['message'] = exc_value.message
            data['traceback'] = u"".join(
                traceback.format_tb(exc_traceback))

        doc = test.test.shortDescription()
        data['name'] = doc if doc else u""
        data.update(kwargs)
        self.storage.add_test_result(self.test_run_id, test.id(), data)

    def addSuccess(self, test, capt=None):
        log.info('SUCCESS for %s' % test)
        if self.discovery:
            data = {}
            doc = test.test.shortDescription()
            data['name'] = doc if doc else ""
            self.storage.add_sets_test(self.test_run_id, test.id(), data)
        else:
            self.stats['passes'] += 1
            self._add_message(test, type='success', taken=self.taken)

    def addFailure(self, test, err, capt=None, tb_info=None):
        log.info('FAILURE for %s' % test)
        self.stats['failures'] += 1
        self._add_message(test, err=err, type='failure', taken=self.taken)

    def addError(self, test, err, capt=None, tb_info=None):
        log.info('TEST NAME: %s\n'
                 'ERROR: %s' % (test, err))
        self.stats['errors'] += 1
        self._add_message(test, err=err, type='error', taken=self.taken)

    def report(self, stream):
        log.info('REPORT')
        if not self.discovery:
            stats_values = sum(self.stats.values())
            self.stats['total'] = stats_values
            self.storage.update_test_run(self.test_run_id, stats=self.stats)

    def beforeTest(self, test):
        self._start_time = time()
        self._add_message(test, type='running')

    @property
    def taken(self):
        if self._start_time:
            return time() - self._start_time
        return 0


class NoseDriver(object):

    def __init__(self):
        log.info('NoseDriver initialized')
        self._pool = pool.Pool(1000)
        self.storage = get_storage()
        self._named_threads = {}

    def check_current_running(self, external_id):
        return external_id in self._named_threads

    def run(self, test_run_id, external_id, conf, **kwargs):
        if 'config_path' in kwargs:
            self.prepare_config(conf, kwargs['config_path'])
        argv_add = kwargs.get('argv', [])
        log.info('Additional args: %s' % argv_add)
        gev = self._pool.spawn(
            self._run_tests, test_run_id, external_id,
            kwargs['test_path'], argv_add)
        self._named_threads[test_run_id] = gev

    def tests_discovery(self, test_set, test_path, argv_add):
        try:
            log.info('Started test discovery %s' % test_set)
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(
                     test_set, self.storage, discovery=True)],
                 exit=False,
                 argv=['tests', '--collect-only']+argv_add)
        except Exception, e:
            log.info('Finished tests discovery %s' % test_set)

    def _run_tests(self, test_run_id, external_id, test_path, argv_add):
        try:
            log.info('Nose Driver spawn green thread for TEST RUN: %s\n'
                     'TEST PATH: %s\n'
                     'ARGS: %s' % (test_run_id, test_path, argv_add))
            main(defaultTest=test_path,
                 addplugins=[StoragePlugin(test_run_id, self.storage)],
                 exit=False,
                 argv=['tests']+argv_add)
            log.info('Test run finished successfully')
            if external_id in self._named_threads:
                del self._named_threads[external_id]
            self.storage.update_test_run(test_run_id, status='finished')
            raise gevent.GreenletExit
        #To close thread we need to catch any exception
        except Exception, e:
            log.info('Close green thread TEST_RUN: %s\n'
                     'Thread closed with exception: %s' % (test_run_id,
                                                           e.message))
            self.storage.update_test_run(test_run_id, status='error')
            if external_id in self._named_threads:
                del self._named_threads[external_id]
            raise gevent.GreenletExit

    def kill(self, test_run_id):
        log.info('Trying to stop process %s\n'
                 '%s' % (test_run_id, self._named_threads))
        if test_run_id in self._named_threads:
            log.info('Kill green thread: %s' % test_run_id)
            self._named_threads[test_run_id].kill()
            del self._named_threads[test_run_id]
            return True
        return False

    def prepare_config(self, conf, testing_config_path):

        conf_path = os.path.abspath(testing_config_path)
        with open(conf_path, 'w') as f:
            for key, value in conf.iteritems():
                f.write(u'%s = %s\n' % (key, value))





