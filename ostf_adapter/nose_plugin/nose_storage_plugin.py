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

from time import time
import logging
import os

from nose.plugins import Plugin
from nose.suite import ContextSuite
from pecan import conf

from ostf_adapter.nose_plugin import nose_utils
from ostf_adapter.storage import get_storage


LOG = logging.getLogger(__name__)


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
        self._start_time = None

    def options(self, parser, env=os.environ):
        LOG.info('NAILGUN HOST %s '
                 'AND PORT %s', conf.nailgun.host, conf.nailgun.port)
        env['NAILGUN_HOST'] = str(conf.nailgun.host)
        env['NAILGUN_PORT'] = str(conf.nailgun.port)
        if self.cluster_id:
            env['CLUSTER_ID'] = str(self.cluster_id)

    def configure(self, options, conf):
        self.conf = conf

    def _add_message(
            self, test, err=None, capt=None,
            tb_info=None, status=None, taken=0):
        data = dict()
        data['name'], data['description'], data['duration'] = \
            nose_utils.get_description(test)
        if err:
            exc_type, exc_value, exc_traceback = err
            LOG.info('Error %s', exc_value)
            data['step'], data['message'] = None, u''
            if not status == 'error':
                data['step'], data['message'] = \
                    nose_utils.format_failure_message(exc_value)
            data['traceback'] = None
        else:
            data['step'], data['message'] = None, None
            data['traceback'] = None
        if isinstance(test, ContextSuite):
            for sub_test in test._tests:
                data['name'], data['description'], data['duration'] = \
                    nose_utils.get_description(test)
                self.storage.add_test_result(
                    self.test_run_id, sub_test.id(), status, taken, data)
        else:
            self.storage.add_test_result(
                self.test_run_id, test.id(), status, taken, data)

    def addSuccess(self, test, capt=None):
        LOG.info('SUCCESS for %s', test)
        if self.discovery:
            data = dict()
            data['name'], data['description'], data['duration'] = \
                nose_utils.get_description(test)
            data['message'] = None
            data['step'] = None
            data['traceback'] = None
            LOG.info('DISCOVERY FOR %s WITH DATA %s', test.id(), data)
            self.storage.add_sets_test(self.test_run_id, test.id(), data)
        else:
            LOG.info('UPDATING TEST %s', test)
            self._add_message(test, status='success', taken=self.taken)

    def addFailure(self, test, err, capt=None, tb_info=None):
        LOG.info('FAILURE for %s', test)
        self._add_message(test, err=err, status='failure', taken=self.taken)

    def addError(self, test, err, capt=None, tb_info=None):
        LOG.info('TEST NAME: %s\n'
                 'ERROR: %s', test, err)
        if err[0] == AssertionError:
            self._add_message(
                test, err=err, status='failure', taken=self.taken)
        else:
            self._add_message(test, err=err, status='error', taken=self.taken)

    def beforeTest(self, test):
        self._start_time = time()
        self._add_message(test, status='running')

    def describeTest(self, test):
        LOG.info('CALLED FOR TEST %s '
                 'DESC %s', test.id(), test.test._testMethodDoc)
        return test.test._testMethodDoc

    @property
    def taken(self):
        if self._start_time:
            return time() - self._start_time
        return 0