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

import time
import httplib
import unittest


class Dummy_test(unittest.TestCase):
    """Class docstring is required?
    """

    def test_fast_pass(self):
        """Ths tests fast pass OK?
        """
        self.assertTrue(True)

    def test_long_pass(self):
        """Will sleep 5 sec
        """
        time.sleep(1)
        self.assertTrue(True)

    def test_fast_fail(self):
        """Fust fail
        """
        self.assertTrue(False, msg='Something goes wroooong')

    def test_fast_error(self):
        """And fast error
        """
        conn = httplib.HTTPSConnection('random.random/random')
        conn.request("GET", "/random.aspx")

    def test_fail_with_step(self):
        self.fail('Step 3 Failed: MEssaasasas')