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

import unittest2
from ostf_adapter.nose_plugin import nose_discovery
from mock import patch, MagicMock
from ostf_adapter.storage import models


stopped__profile__ = {
    "id": "stopped_test",
    "driver": "nose",
    "test_path": "functional/dummy_tests/stopped_test.py",
    "description": "Long running 25 secs fake tests"
}
general__profile__ = {
    "id": "general_test",
    "driver": "nose",
    "test_path": "functional/dummy_tests/general_test.py",
    "description": "General fake tests"
}


@patch('ostf_adapter.nose_plugin.nose_discovery.storage')
class TestNoseDiscovery(unittest2.TestCase):

    def setUp(self):
        self.fixtures = [models.TestSet(**stopped__profile__),
                         models.TestSet(**general__profile__)]
        self.fixtures_iter = iter(self.fixtures)
        self.storage = MagicMock()

    def test_discovery(self, storage_mock):
        storage_mock.get_storage.return_value = self.storage
        self.storage.add_test_set.side_effect = \
            lambda *args, **kwargs: next(self.fixtures_iter)
        nose_discovery.discovery(path='functional/dummy_tests')
        self.assertEqual(self.storage.add_test_set.call_count, 2)
        self.assertEqual(self.storage.add_test_for_testset.call_count, 8)

