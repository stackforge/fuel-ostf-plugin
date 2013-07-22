__author__ = 'ekonstantinov'
import unittest
import time
from client import TestingAdapterClient
from config import CONFIG


class SubsetException(Exception):
    pass


class adapter_tests(unittest.TestCase):

    def _verify_json(self, assertions, json):
        """For the given json response verify that assertions are present
        """
        for item in json:
            for subitem in assertions:
                if item['testset'] == subitem['testset']:
                    for s in subitem['tests']:
                        if s['id'] not in (i['id'] for i in item['tests']):
                            raise AssertionError('{} not in:\n{}'.format(s['id'], [i['id'] for i in item['tests']]))

        def is_subset(item, subset):
            if type(item) != type(subset) and type(subset) not in (str, unicode):
                return False
            if type(subset) is list:

                return all(is_subset(i, s) for i in item for s in subset if i.get('id') == s.get('id') or s.get('id') == None)
            elif type(subset) is dict:
                try:
                    return all(is_subset(item[s], subset[s]) for s in subset)
                except AssertionError as e:
                    real, expected = e.message.split('|')
                    key = [x for x in subset if subset[x] == expected][0]
                    msg = '"{}" was found, when "{}" was excepted in key = "{}"'.format(real, expected, key)
                    #msg = '{}\n{}'.format(item,subset)
                    raise SubsetException(msg)
            else:
                msg = '{item}|{subset}'.format(item=item, subset=subset)
                assert item == subset, msg
                return item == subset

        msg = '{subset}     IS NOT IN     {item}'.format(subset=assertions, item=json)
        try:
            self.assertTrue(is_subset(json, assertions), msg)
        except SubsetException as e:
            msg = '{}\nwith response:\n{}\nand assertion:\n{}'.format(e.message, json, assertions)
            raise AssertionError(msg)

    def _verify_json_status(self, json):
        """Helper to verify that json responce contains information about tests either for defined testset,
         or for all test in json response. Verification is done against global self.testsets dict"""
        for item in json:

            msg = '"{item}" do no contain "testset"\n{json}'.format(item=item,json=json)

            self.assertTrue(item.get('testset', None) is not None, msg)
            test_set = item['testset']
            for test in self.testsets[test_set]:
                self.assertTrue(self.tests[test] in (item['id'] for item in item['tests']))

    @classmethod
    def setUp(cls):
        url = 'http://172.18.198.75:8989/v1'
        #url = 'http://172.18.198.75:9999/ostf'
        cls.adapter = TestingAdapterClient(url)
        cls.tests = {
            'fast_pass': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
            'fast_error': 'functional.dummy_tests.general_test.Dummy_test.test_fast_error',
            'fast_fail': 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail',
            'long_pass': 'functional.dummy_tests.general_test.Dummy_test.test_long_pass',
            'fail_step': 'functional.dummy_tests.general_test.Dummy_test.test_fail_with_step',
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
        """Verify that self.testsets are in json response
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
        """Verify that test status changes in time from running to success
        """
        testset = "plugin_general"
        cluster_id = 1
        self.adapter.start_testrun(testset, cluster_id)
        time.sleep(2)
        json = self.adapter.testruns_last(cluster_id)
        assertions = [
            {'status': 'running',
                'tests': [
                    {'id': self.tests['fast_pass'],
                        'name': 'Ths tests fast pass OK?',
                        'status': 'success'},
                    {'id': self.tests['long_pass'],
                        'description': '        ',
                        'status': 'running'},
                    {'id': self.tests['fail_step'],
                        'message': 'MEssaasasas',
                        'status': 'failure'},
                    {'id': self.tests['fast_error'],
                        'message': '',
                        'status': 'error'},
                    {'id': self.tests['fast_fail'],
                        'message': 'Something goes wroooong',
                        'status': 'failure'}],
                'testset': 'plugin_general'}]
        self._verify_json(assertions, json)
        time.sleep(25)
        json = self.adapter.testruns_last(cluster_id)
        assertions[0]['status'] = 'finished'
        assertions[0]['tests'][1]['status'] = 'success'
        self._verify_json(assertions, json)

    def test_stopped_testset(self):
        """Verify that long running testrun can be stopped
        """
        testset = "plugin_stopped"
        cluster_id = 2
        json = self.adapter.start_testrun(testset, cluster_id)
        current_id = json[0]['id']
        time.sleep(15)
        json = self.adapter.testruns_last(cluster_id)
        assertions = [
            {'status': 'running',
                'tests': [
                    {'id': self.tests['not_long'],
                        'status': 'success'},
                    {'id': self.tests['so_long'],
                        'status': 'success'},
                    {'id': self.tests['really_long'],
                        'status': 'running'}],
                'testset': 'plugin_stopped'}]
        self._verify_json(assertions, json)
        self.adapter.stop_testrun(current_id)
        json = self.adapter.testruns_last(cluster_id)
        assertions[0]['status'] = 'stopped'
        assertions[0]['tests'][2]['status'] = 'stopped'
        self._verify_json(assertions, json)

    def test_testruns(self):
        """Verify that you can't start new testrun for the same cluster_id while previous run is running"""
        testsets = {"plugin_stopped": None,
                    "plugin_general": None}
        cluster_id = 3
        for testset in testsets:
            self.adapter.start_testrun(testset, cluster_id)
        self.adapter.testruns_last(cluster_id)

        for testset in testsets:
            json = self.adapter.start_testrun(testset, cluster_id)

            msg = "Response '{json}' is not empty when you try to start testrun" \
                " with testset and cluster_id that are already running".format(json=json)

            self.assertTrue(json == [{}], msg)

    def test_load_runs(self):
        """Verify that you can start 20 testruns in a row with different cluster_id"""
        testset = "plugin_general"
        json = self.adapter.testruns()
        last_test_run = max(item['id'] for item in json)
        self.assertTrue(last_test_run == len(json))

        for cluster_id in xrange(100, 105):
            json = self.adapter.start_testrun(testset, cluster_id)

            msg = 'Response for start_testset("{testset}", "{cluster_id}") was empty = {json}'.\
                format(testset=testset, cluster_id=cluster_id, json=json)

            self.assertTrue(json != [{}], msg)

        '''TODO: Rewrite assertions to verity that all 5 testruns ended with appropriate status'''

        json = self.adapter.testruns()
        last_test_run = max(item['id'] for item in json)
        self.assertTrue(last_test_run == len(json))

    def test_single_test_run(self):
        """Verify that you can run individual tests from given testset"""
        testset = "plugin_general"
        tests = ['functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
                 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail']
        cluster_id = 50
        json = self.adapter.start_testrun_tests(testset, tests, cluster_id)
        assertions = [
            {'status': 'started', 'tests': [
                {'status': 'disabled',
                 'id': self.tests['fast_error']},
                {'status': 'wait_running',
                 'id': self.tests['fast_fail']},
                {'status': 'wait_running',
                 'id': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass'},
                {'status': 'disabled',
                 'id': self.tests['long_pass']}],
             'testset': 'plugin_general'}]
        self._verify_json(assertions, json)
        time.sleep(5)
        json = self.adapter.testruns_last(cluster_id)
        assertions = [
            {'status': 'finished', 'tests': [
                {'status': 'disabled',
                 'id': self.tests['fast_error']},
                {'status': 'failure',
                 'id': self.tests['fast_fail']},
                {'status': 'success',
                 'id': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass'},
                {'status': 'disabled',
                 'id': self.tests['long_pass']}],
             'testset': 'plugin_general'}]
        self._verify_json(assertions, json)

    def test_single_test_restart(self):
        """Verify that you restart individual tests for given testrun"""
        testset = "plugin_general"
        tests = ['functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
                 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail']
        cluster_id = 60

        json = self.adapter.start_testrun(testset, cluster_id)
        current_id = json[0]['id']
        time.sleep(25)

        json = self.adapter.restart_tests(tests, current_id)
        assertions = [
            {'status': 'restarted',
                'tests': [
                    {'id': self.tests['fast_pass'],
                        'status': 'wait_running'},
                    {'id': self.tests['long_pass'],
                        'status': 'success'},
                    {'id': self.tests['fast_error'],
                        'status': 'error'},
                    {'id': self.tests['fast_fail'],
                        'status': 'wait_running'}],
                'testset': 'plugin_general'}]
        self._verify_json(assertions, json)
        time.sleep(5)
        json = self.adapter.testruns_last(cluster_id)
        assertions = [
            {'status': 'finished',
                'tests': [
                    {'id': self.tests['fast_pass'],
                        'status': 'success'},
                    {'id': self.tests['long_pass'],
                        'status': 'success'},
                    {'id': self.tests['fast_error'],
                        'status': 'error'},
                    {'id': self.tests['fast_fail'],
                        'status': 'failure'}],
                'testset': 'plugin_general'}]
        self._verify_json(assertions, json)

    def test_restart_combinations(self):
        """Verify that you can restart both tests that ran and did not run during single test start"""
        testset = "plugin_general"
        tests = ['functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
                 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail']
        disabled_test = ['functional.dummy_tests.general_test.Dummy_test.test_fast_error', ]
        cluster_id = 70

        json = self.adapter.start_testrun_tests(testset, tests, cluster_id)
        current_id = json[0]['id']
        time.sleep(5)

        json = self.adapter.restart_tests(tests, current_id)
        assertions = [
            {'status': 'restarted', 'tests': [
                {'status': 'disabled',
                 'id': self.tests['fast_error']},
                {'status': 'wait_running',
                 'id': self.tests['fast_fail']},
                {'status': 'wait_running',
                 'id': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass'},
                {'status': 'disabled',
                 'id': self.tests['long_pass']}],
             'testset': 'plugin_general'}]
        self._verify_json(assertions, json)
        time.sleep(5)
        json = self.adapter.testruns_last(cluster_id)
        assertions = [
            {'status': 'finished', 'tests': [
                {'status': 'disabled',
                 'id': self.tests['fast_error']},
                {'status': 'failure',
                 'id': self.tests['fast_fail']},
                {'status': 'success',
                 'id': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass'},
                {'status': 'disabled',
                 'id': self.tests['long_pass']}],
             'testset': 'plugin_general'}]
        self._verify_json(assertions, json)

        json = self.adapter.restart_tests(disabled_test, current_id)
        assertions = [
            {'status': 'restarted', 'tests': [
                {'status': 'wait_running',
                 'id': self.tests['fast_error']},
                {'status': 'failure',
                 'id': self.tests['fast_fail']},
                {'status': 'success',
                 'id': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass'},
                {'status': 'disabled',
                 'id': self.tests['long_pass']}],
             'testset': 'plugin_general'}]
        self._verify_json(assertions, json)
        time.sleep(15)
        json = self.adapter.testruns_last(cluster_id)
        assertions = [
            {'status': 'finished', 'tests': [
                {'status': 'error',
                 'id': self.tests['fast_error']},
                {'status': 'failure',
                 'id': self.tests['fast_fail']},
                {'status': 'success',
                 'id': self.tests['fast_pass']},
                {'status': 'disabled',
                 'id': self.tests['long_pass']}],
             'testset': 'plugin_general'}]
        self._verify_json(assertions, json)

    def test_restart_during_run(self):
        testset = 'plugin_general'
        tests = ['functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
                 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail',
                 self.tests['long_pass']]
        cluster_id = 999

        self.adapter.start_testrun(testset, cluster_id)
        time.sleep(2)
        json = self.adapter.restart_tests_last(testset, tests, cluster_id)
        msg = 'Response was not empty after trying to restart running testset:\n {}'.format(json)
        self.assertTrue(json == [{}], msg)

    def test_sanity_scenario(self):
        testset = "fuel_sanity"
        cluster_id = 3
        tests = []
        timeout = 60

        from pprint import pprint

        for i in range(1):
            result = self.adapter.run_and_timeout_unless_finished('run', testset, tests, cluster_id, timeout)
            pprint(result)
            if result['status'] == 'running':
                running_tests = [test for test in result['tests']
                                 if result['tests'][test][0] in ['running', 'wait_running']]
                print "restarting: ", running_tests
                result = self.adapter.run_and_timeout_unless_finished('restart', testset, running_tests, cluster_id, timeout)
                print 'Restart', result, '\n'














        #self.assertFalse(json)





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




