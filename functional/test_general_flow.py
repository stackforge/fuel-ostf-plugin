__author__ = 'ekonstantinov'
import unittest
import time
from client import TestingAdapterClient
from config import CONFIG


class adapter_tests(unittest.TestCase):

    def _verify_json(self, assertions, json):
        """For the given json response verify that assertions are present
        """

        for test in json['tests']:
            if test['id'] in assertions:
                items = assertions[test['id']]
                for item in items:
                    msg = '"{test}" had "{actual}" value in "{item}", while "{expected}" value was expected'\
                        .format(test=test['id'], item=item, actual=test.get(item).capitalize(), expected=items.get(item).capitalize())
                    self.assertTrue(items[item] == test.get(item), msg)

    def _verify_json_status(self, json, testset=None):
        for item in json:
            test_set = testset if testset else item['testset']
            for test in self.testsets[test_set]:
                self.assertTrue(self.tests[test] in (item['id'] for item in item['tests']))

    @classmethod
    def setUp(cls):
        url = 'http://0.0.0.0:8989/v1'
        cls.adapter = TestingAdapterClient(url)
        cls.tests = {
            'fast_pass': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
            'fast_error': 'functional.dummy_tests.general_test.Dummy_test.test_fast_error',
            'fast_fail': 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail',
            'long_pass': 'functional.dummy_tests.general_test.Dummy_test.test_long_pass',
            'really_long': 'functional.dummy_tests.stopped_test.dummy_tests_stopped.test_really_long',
            'not_long': 'functional.dummy_tests.stopped_test.dummy_tests_stopped.test_not_long_at_all',
            'so_long': 'functional.dummy_tests.stopped_test.dummy_tests_stopped.test_one_no_so_long'

        }
        cls.testsets = {
            "fuel_smoke": None,
            "fuel_sanity": None,
            "plugin_general": ['fast_pass', 'fast_error', 'fast_fail', 'long_pass'],
            "plugin_stopped": ['really_long', 'not_long', 'so_long']
        }

    def test_list_testsets(self):
        """Verify that self.testsets are in json respons
        """
        json = self.adapter.testsets()
        for testset in self.testsets:
            response_testsets = [item['id'] for item in json]
            msg = '"{test}" not in "{response}"'.format(test=testset, response=response_testsets)
            self.assertTrue(testset in response_testsets, msg)

    def test_list_tests(self):
        """Verify that self.tests are in json response
        """
        json = self.adapter.tests()
        for test in self.tests.values():
            response_tests = [item['id'] for item in json]
            msg = '"{test}" not in "{response}"'.format(test=test.capitalize(), response=response_tests)
            self.assertTrue(test in response_tests, msg)

    def test_general_testset(self):
        """Send start_testrun
        wait for 5 sec
        check status: expected
        """
        testset = "plugin_general"
        config = {}
        cluster_id = 1
        json = self.adapter.start_testrun(testset, config, cluster_id)
        self._verify_json_status(json)
        time.sleep(5)
        json = self.adapter.testruns_last(cluster_id)[0]
        assertions = {
            self.tests['fast_pass']:  {'status': 'success'},
            self.tests['not_long']:  {'status': 'running'},
            self.tests['fast_error']: {'status': 'error', 'message': "[Errno -2] Name or service not known"},
            self.tests['fast_fail']:  {'status': 'failure', 'message': 'Something goes wroooong'}
        }
        self._verify_json(assertions, json)
        time.sleep(15)
        json = self.adapter.testruns_last(cluster_id)[0]
        assertions[self.tests['not_long']]['status'] = 'success'
        self._verify_json(assertions, json)

    def test_stopped_testset(self):
        testset = "plugin_stopped"
        config = {}
        cluster_id = 2
        json = self.adapter.start_testrun(testset, config, cluster_id)[0]
        current_id = json['id']
        time.sleep(15)
        json = self.adapter.testruns_last(cluster_id)[0]
        assertions = {
            self.tests['really_long']:  {'status': 'running'},
            self.tests['not_long']:     {'status': 'success'},
            self.tests['so_long']:      {'status': 'success'}
        }
        self._verify_json(assertions, json)
        self.adapter.stop_testrun(current_id)
        json = self.adapter.testruns_last(cluster_id)[0]
        assertions[self.tests['really_long']]['status'] = 'stopped'
        self._verify_json(assertions, json)

    def test_testruns(self):
        testsets = {"plugin_stopped": None,
                    "plugin_general": None}
        config = {}
        cluster_id = 3
        for testset in testsets:
            json = self.adapter.start_testrun(testset, config, cluster_id)
            self._verify_json_status(json, testset=testset)
        json = self.adapter.testruns_last(cluster_id)
        self._verify_json_status(json)

        for testset in testsets:
            json = self.adapter.start_testrun(testset, config, cluster_id)
            self.assertTrue(all(not item for item in json))

    def test_load_runs(self):
        testset = "plugin_general"
        config = {}
        json = self.adapter.testruns()

        last_test_run = max(item['id'] for item in json)
        self.assertTrue(last_test_run == len(json))
        for cluster_id in xrange(20):
            json = self.adapter.start_testrun(testset, config, cluster_id)
            self._verify_json_status(json, testset=testset)
        json = self.adapter.testruns()
        last_test_run = max(item['id'] for item in json)
        self.assertTrue(last_test_run == len(json))



    """   def test_long_work(self):
        config = CONFIG
        testset = "fuel_sanity"
        cluster_id = 11
        json = self.adapter.start_testrun(testset, config, cluster_id)
        #self.assertFalse(json)"""

    """def _wait_for(self, event, state, state_finder, timeout, stop_sequence):
        start_time = int(time.time())
        evnt = None
        while 1:
            try:
                evnt = event()
            except Exception:
                pass
            if state_finder(evnt) == state:
                    return evnt
            if (int(time.time()) - start_time) >= timeout:
                try:
                    stop_sequence()
                except Exception:
                    return "Failed"
                return "Stopped"

    def run_test_set_and_wait_for_finished(self, testset, config):
        state = "finished"
        def state_finder(submitie):
            status = [y['status'] for y in submitie if y['testset'] == 'fuel_sanity']
            return status[0] if status else None"""




