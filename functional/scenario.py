__author__ = 'ekonstantinov'
from functional.base import BaseAdapterTest, Response

import time


class ScenarioTests(BaseAdapterTest):
    @classmethod
    def setUpClass(cls):
        url = 'http://172.18.198.75:8989/v1'
        mapping = {}

        cls.client = cls.init_client(url, mapping)

    def test_random_scenario(self):
        testset = "fuel_sanity"
        cluster_id = 3
        tests = []
        timeout = 60

        from pprint import pprint

        for i in range(1):
            r = self.client.run_with_timeout(testset, tests, cluster_id, timeout)
            pprint([item for item in r.test_sets[testset]['tests']])
            if r.fuel_sanity['status'] == 'stopped':
                running_tests = [test for test in r._tests
                                 if r._tests[test]['status'] is 'stopped']
                print "restarting: ", running_tests
                result = self.client.restart_with_timeout(testset, running_tests, cluster_id, timeout)
                print 'Restart', result

    def test_run_fuel_sanity(self):
        testset = "fuel_sanity"
        cluster_id = 3
        tests = []
        timeout = 120

        r = self.client.run_with_timeout(testset, tests, cluster_id, timeout)
        self.assertEqual(r.fuel_sanity['status'], 'finished')

    def test_run_fuel_smoke(self):
        testset = "fuel_smoke"
        cluster_id = 3
        tests = []
        timeout = 480

        r = self.client.run_with_timeout(testset, tests, cluster_id, timeout)
        self.assertEqual(r.fuel_smoke['status'], 'finished')