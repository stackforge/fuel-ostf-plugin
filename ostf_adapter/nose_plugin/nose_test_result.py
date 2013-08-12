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

import sys
from nose import core
from nose import result


class StorageTestRunner(core.TextTestRunner):

    def _makeResult(self):
        return StorageTestResult(
            self.stream,
            self.descriptions,
            config=self.config)


class StorageTestResult(result.TextTestResult):

    def __init__(self, stream, descriptions, verbosity=0, config=None,
                 errorClasses=None):
        if errorClasses is None:
            errorClasses = {}
        self.errorClasses = errorClasses
        self.config = config
        super(StorageTestResult, self).__init__(
            stream, descriptions, verbosity)

    def addSkip(self, test, reason):
        # 2.7 skip compat
        pass

    def addError(self, test, err):
        """Overrides normal addError to add support for
        errorClasses. If the exception is a registered class, the
        error will be added to the list for that class, not errors.
        """
        pass

    def addSuccess(self, test):
        pass

    # override to bypass changes in 2.7
    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def printLabel(self, label, err=None):
        # Might get patched into a streamless result
        pass

    def printErrors(self):
        """Overrides to print all errorClasses errors as well.
        """
        pass

    def printSummary(self, start, stop):
        """Called by the test runner to print the final summary of test
        run results.
        """
        pass

    def wasSuccessful(self):
        """Overrides to check that there are no errors in errorClasses
        lists that are marked as errors and should cause a run to
        fail.
        """
        return True

    def _addError(self, test, err):
        pass


class OstfTestProgram(core.TestProgram):

    def __init__(self, cluster_id, test_run_id=None, test_set=None,
                 *args, **kwargs):
        self.cluster_id = cluster_id
        self.test_run_id = test_run_id
        self.test_set = test_set
        super(OstfTestProgram, self).__init__(*args, **kwargs)

    def runTests(self):
        if self.testRunner is None:
            self.testRunner = StorageTestRunner(
                stream=self.config.stream,
                config=self.config
            )
        plug_runner = self.config.plugins.prepareTestRunner(self.testRunner)
        if plug_runner is not None:
            self.testRunner = plug_runner
        result = self.testRunner.run(self.test)
        self.success = result.wasSuccessful()
        if self.exit:
            sys.exit(not self.success)
        return self.success