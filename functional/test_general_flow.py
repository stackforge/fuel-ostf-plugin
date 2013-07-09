__author__ = 'ekonstantinov'
import unittest
import requests
import time
from client import TestingAdapterClient


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

    def setUp(self):
        url = 'http://172.18.164.69:8989/v1'
        self.adapter = TestingAdapterClient(url)
        self.tests = {
            'fast_pass': 'functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
            'fast_error': 'functional.dummy_tests.general_test.Dummy_test.test_fast_error',
            'fast_fail': 'functional.dummy_tests.general_test.Dummy_test.test_fast_fail',
            'long_pass': 'functional.dummy_tests.general_test.Dummy_test.test_long_pass',
            'really_long': 'functional.dummy_tests.stopped_test.dummy_tests_stopped.test_really_long',
            'not_long': 'functional.dummy_tests.stopped_test.dummy_tests_stopped.test_not_long_at_all',
            'so_long': 'functional.dummy_tests.stopped_test.dummy_tests_stopped.test_one_no_so_long'

        }
        self.testsets = [
            "fuel_smoke",
            "fuel_sanity",
            "plugin_general",
            "plugin_stopped"
        ]

    def test_list_testsets(self):
        """Verify that self.testsets are in json respons
        """
        json = self.adapter.testsets()
        self.assertTrue(all(x in (item['id'] for item in json) for x in self.testsets))

    def test_list_tests(self):
        """Verify that self.tests are in json response
        """
        json = self.adapter.tests()
        self.assertTrue(all(x in (item['id'] for item in json) for x in self.tests.values()))

    def test_general_testset(self):
        """Send start_testrun
        wait
        """
        testset = "plugin_general"
        config = {}
        cluster_id = 1
        self.adapter.start_testrun(testset, config, cluster_id)
        time.sleep(5)
        json = self.adapter.testruns_last(cluster_id)
        assertions = {
            self.tests['fast_pass']:  {'status': 'success'},
            self.tests['not_long']:  {'status': 'running'},
            self.tests['fast_error']: {'status': 'error', 'message': "[Errno -2] Name or service not known"},
            self.tests['fast_fail']:  {'status': 'failure', 'message': 'Something goes wroooong'}
        }
        self._verify_json(assertions, json)
        time.sleep(15)
        assertions[self.tests['fast_pass']]['status'] = 'success'
        self._verify_json(assertions, json)

    def test_stopped_testset(self):
        testset = "plugin_stopped"
        config = {}
        cluster_id = 2
        self.adapter.start_testrun(testset, config, cluster_id)
        time.sleep(15)
        json = self.adapter.testruns_last(cluster_id)
        current_id = json['id']
        assertions = {
            self.tests['really_long']:  {'status': 'running'},
            self.tests['not_long']:     {'status': 'success'},
            self.tests['so_long']:      {'status': 'success'}
        }
        self._verify_json(assertions, json)
        self.adapter.stop_testrun(current_id)
        json = self.adapter.testruns_last(cluster_id)
        assertions[self.tests['really_long']]['status'] = 'stopped'
        self._verify_json(assertions, json)






"""
        r = requests.post(self.general, headers=self.headers)
        self.assertEquals(200, r.status_code)
        json_out = r.json()
        self.assertEquals('plugin-general', json_out['type'])
        self.id = json_out['id']
        host = ''.join((self.general, '/', str(self.id)))
        time.sleep(2)
        r = requests.get(host, headers=self.headers)
        self.assertEquals(200, r.status_code)
        json_out = r.json()

        assertions = {
            ':'.join(('tests', self.tests['fast_pass'], 'type')): 'success',
            #':'.join(('tests', self.tests['long_pass'], 'type')): 'running',
            ':'.join(('tests', self.tests['fast_error'], 'type')): 'error',
            ':'.join(('tests', self.tests['fast_error'], 'exc_type')): 'DNSError',
            ':'.join(('tests', self.tests['fast_fail'], 'type')): 'failure',
            ':'.join(('tests', self.tests['fast_fail'], 'exc_type')): 'AssertionError'
        }
        self.verify_json(assertions, json_out)
        time.sleep(5)

        r = requests.get(host, headers=self.headers)
        self.assertEquals(200, r.status_code)
        json_out = r.json()
        assertions = {
            ':'.join(('tests', self.tests['fast_pass'],     'type')):      'success',
            ':'.join(('tests', self.tests['long_pass'],     'type')):      'success',
            ':'.join(('tests', self.tests['fast_error'],    'type')):      'error',
            ':'.join(('tests', self.tests['fast_error'],    'exc_type')):  'DNSError',
            ':'.join(('tests', self.tests['fast_fail'],     'type')):      'failure',
            ':'.join(('tests', self.tests['fast_fail'],     'exc_type')):  'AssertionError'
        }
        self.verify_json(assertions, json_out)

        previous_run = host
        r = requests.post(self.general, headers=self.headers)
        self.assertEquals(200, r.status_code)

    def test_stop_task(self):
        r = requests.post(self.stopped, headers=self.headers)
        self.assertEquals(200, r.status_code)
        json_out = r.json()
        self.assertEquals('plugin-stopped', json_out['type'])
        self.id = json_out['id']
        host = ''.join((self.stopped, '/', str(self.id)))
        time.sleep(1)
        r = requests.get(host, headers=self.headers)
        self.assertEquals(200, r.status_code)
        json_out = r.json()
        asserties = {
            ':'.join(('tests', self.tests['really_long'], 'type')): 'running'}
        #self.verify_json(asserties, json_out)
        r = requests.delete(host, headers=self.headers)
        self.assertEquals(200, r.status_code)
        message = 'Killed test run with ID {id}'.format(id=self.id)
        json_out = r.json()
        self.assertEquals(message, json_out['message'])
"""