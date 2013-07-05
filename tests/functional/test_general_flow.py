__author__ = 'ekonstantinov'
import unittest
import requests
import time
from collections import Iterable
import collections


class TestingAdapterClient(object):
    def __init__(self, url):
        self.url = url

    def request(self, method, url, data=None):
        headers = {'content-type': 'application/json'}
        r = requests.request(method, url, data=data, headers=headers)
        if 2 != r.status_code/100:
            raise AssertionError('{url} responded with {code}'.format(usrl=url, code=r.status_code))
        return r.json()

    def testsets(self):
        url = ''.join([self.url, '/testsets'])
        return self.request('GET', url)

    def tests(self):
        url = ''.join([self.url, '/tests'])
        return self.request('GET', url)

    def testruns(self):
        url = ''.join([self.url, '/testruns'])
        return self.request('GET', url)

    def __getattr__(self, item):
        getters = ['testsets', 'tests', 'testruns']
        if item in getters:
            url = ''.join([self.url, '/', item])
            return lambda: self.request('GET', url)








    def verify_json(self, asserties, json):
        for assertie in asserties:
            name = assertie.split(':')
            res = json
            while name:
                res = res[name.pop(0)]
            self.assertEquals(asserties[assertie], res)

    def setUp(self):
        self.headers = {}
        self.url = 'http://localhost:8777/v1/'
        self.general = '{url}plugin-general'.format(url=self.url)
        self.stopped = '{url}plugin-stopped'.format(url=self.url)
        self.tests = {
            'fast_pass': 'tests.functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
            'fast_error': 'tests.functional.dummy_tests.general_test.Dummy_test.test_fast_error',
            'fast_fail': 'tests.functional.dummy_tests.general_test.Dummy_test.test_fast_fail',
            'long_pass': 'tests.functional.dummy_tests.general_test.Dummy_test.test_long_pass',
            'really_long': 'tests.functional.dummy_tests.stopped_test.dummy_tests_stopped.test_really_long'
        }

    def test_assign_task(self):
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

        asserties = {
            ':'.join(('tests', self.tests['fast_pass'], 'type')): 'success',
            #':'.join(('tests', self.tests['long_pass'], 'type')): 'running',
            ':'.join(('tests', self.tests['fast_error'], 'type')): 'error',
            ':'.join(('tests', self.tests['fast_error'], 'exc_type')): 'DNSError',
            ':'.join(('tests', self.tests['fast_fail'], 'type')): 'failure',
            ':'.join(('tests', self.tests['fast_fail'], 'exc_type')): 'AssertionError'
        }
        self.verify_json(asserties, json_out)
        time.sleep(5)

        r = requests.get(host, headers=self.headers)
        self.assertEquals(200, r.status_code)
        json_out = r.json()
        asserties = {
            ':'.join(('tests', self.tests['fast_pass'],     'type')):      'success',
            ':'.join(('tests', self.tests['long_pass'],     'type')):      'success',
            ':'.join(('tests', self.tests['fast_error'],    'type')):      'error',
            ':'.join(('tests', self.tests['fast_error'],    'exc_type')):  'DNSError',
            ':'.join(('tests', self.tests['fast_fail'],     'type')):      'failure',
            ':'.join(('tests', self.tests['fast_fail'],     'exc_type')):  'AssertionError'
        }
        self.verify_json(asserties, json_out)

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
