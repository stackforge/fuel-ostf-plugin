__author__ = 'ekonstantinov'
import unittest
import requests
import time
from client import TestingAdapterClient


class adapter_tests(unittest.TestCase):

    def verify_json(self, assertions, json):
        for assertion in assertions:
            path = assertion.split(':')
            res = json
            while path:
                res = res[path.pop(0)]
            self.assertEquals(assertions[assertion], res)

    def setUp(self):
        url = 'http://172.18.164.69:8989/v1'
        self.adapter = TestingAdapterClient(url)
        self.tests = {
            'fast_pass': 'tests.functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
            'fast_error': 'tests.functional.dummy_tests.general_test.Dummy_test.test_fast_error',
            'fast_fail': 'tests.functional.dummy_tests.general_test.Dummy_test.test_fast_fail',
            'long_pass': 'tests.functional.dummy_tests.general_test.Dummy_test.test_long_pass',
            'really_long': 'tests.functional.dummy_tests.stopped_test.dummy_tests_stopped.test_really_long'
        }
        self.testsets = [
            "fuel_smoke",
            "fuel_sanity",
            "plugin-general",
            "plugin-stopped"
        ]

    def test_list_testruns(self):
        json = self.adapter.testruns()
        self.assertTrue(all(x in (item['id'] for item in json) for x in self.tests))

    def test_list_tests(self):
        json = self.adapter.tests()
        self.assertTrue(all(x in (item['id'] for item in json) for x in self.tests.values()))

    def test_general_testset(self):
        testset = "plugin-general"
        metadata = ""
        json = self.adapter.start_testrun(testset, metadata)
        assertions = {
            ':'.join(('tests', self.tests['fast_pass'], 'type')): 'success',
            ':'.join(('tests', self.tests['long_pass'], 'type')): 'running',
            ':'.join(('tests', self.tests['fast_error'], 'type')): 'error',
            ':'.join(('tests', self.tests['fast_error'], 'exc_type')): 'DNSError',
            ':'.join(('tests', self.tests['fast_fail'], 'type')): 'failure',
            ':'.join(('tests', self.tests['fast_fail'], 'exc_type')): 'AssertionError'
        }
        self.verify_json(assertions, json)
        time.sleep(5)
        assertions[':'.join(('tests', self.tests['long_pass'], 'type'))] = 'success'
        self.verify_json(assertions, json)


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