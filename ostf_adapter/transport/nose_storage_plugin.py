from nose.plugins import Plugin
from nose.suite import ContextSuite
from time import time
import logging
from ostf_adapter.transport import nose_utils
from ostf_adapter.storage import get_storage
import os
from pecan import conf


TESTS_PROCESS = {}


log = logging.getLogger(__name__)


class StoragePlugin(Plugin):

    enabled = True
    name = 'storage'
    score = 15000

    def __init__(
            self, test_run_id, cluster_id, discovery=False):
        self._capture = []
        self.test_run_id = test_run_id
        self.cluster_id = cluster_id
        self.storage = get_storage()
        self.discovery = discovery
        super(StoragePlugin, self).__init__()
        log.info('Storage Plugin initialized')
        self._start_time = None
        self._started = False

    def options(self, parser, env=os.environ):
        log.info('NAILGUN HOST %s '
                 'AND PORT %s' % (conf.nailgun.host, conf.nailgun.port))
        env['NAILGUN_HOST'] = str(conf.nailgun.host)
        env['NAILGUN_PORT'] = str(conf.nailgun.port)
        if self.cluster_id:
            env['CLUSTER_ID'] = str(self.cluster_id)

    def configure(self, options, conf):
        self.conf = conf

    def _add_message(
            self, test, err=None, capt=None,
            tb_info=None, status=None, taken=0):
        if not self._started:
            self.storage.update_test_run(self.test_run_id, status='running')
        self._started = True
        data = dict()
        data['name'], data['description'], data['duration'] =\
            nose_utils.get_description(test)
        if err:
            exc_type, exc_value, exc_traceback = err
            log.info('Error %s' % exc_value)
            data['message'] = u''
            if not status == 'error':
                data['step'], data['message'] =\
                    nose_utils.format_failure_message(exc_value)
            data['traceback'] = nose_utils.format_exception(err)
        else:
            data['step'], data['message'] = None, None
            data['traceback'] = None
        if isinstance(test, ContextSuite):
            for sub_test in test._tests:
                data['name'], data['description'], data['duration'] =\
                    nose_utils.get_description(test)
                self.storage.add_test_result(
                    self.test_run_id, sub_test.id(), status, taken, data)
        else:
            self.storage.add_test_result(
                self.test_run_id, test.id(), status, taken, data)

    def addSuccess(self, test, capt=None):
        log.info('SUCCESS for %s' % test)
        if self.discovery:
            data = dict()
            data['name'], data['description'], data['duration'] =\
                nose_utils.get_description(test)
            data['message'] = None
            data['traceback'] = None
            log.info('DISCOVERY FOR %s WITH DATA %s' % (test.id(), data))
            self.storage.add_sets_test(self.test_run_id, test.id(), data)
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