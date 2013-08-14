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

from nose import plugins
import logging
import os

from ostf_adapter import storage
from ostf_adapter.nose_plugin import nose_storage_plugin
from ostf_adapter.nose_plugin import nose_test_runner
from ostf_adapter.nose_plugin import nose_utils


CORE_PATH = 'fuel_health'

LOG = logging.getLogger(__name__)


class DiscoveryPlugin(plugins.Plugin):

    enabled = True
    name = 'storage'
    score = 15000

    def __init__(self):
        self.storage = storage.get_storage()
        self.test_sets = {}
        super(DiscoveryPlugin, self).__init__()

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        pass

    def afterImport(self, filename, module):
        module = __import__(module, fromlist=[module])
        if hasattr(module, '__profile__'):
            LOG.info('%s discovered.', module.__name__)
            test_set = self.storage.add_test_set(module.__profile__)
            self.test_sets[test_set.id] = test_set

    def addSuccess(self, test):
        test_id = test.id()
        for test_set_id in self.test_sets.keys():
            if test_set_id in test_id:
                LOG.info('%s added for %s', test_id, test_set_id)
                data = dict()
                data['title'], data['description'], data['duration'] = \
                    nose_utils.get_description(test)
                self.storage.add_test_for_testset(
                    test_set_id, test_id, data)


def discovery(path=None):
    """
        function to automaticly discover any test packages
    """
    nose_test_runner.SilentTestProgram(
            defaultTest=path,
            addplugins=[DiscoveryPlugin()],
            exit=False,
            argv=['tests_discovery','--collect-only', '--q'])