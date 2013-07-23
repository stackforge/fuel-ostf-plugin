__author__ = 'ekonstantinov'
import requests
from json import dumps
import time
import logging


class TestingAdapterClient(object):
    def __init__(self, url):
        self.url = url

    def _request(self, method, url, data=None):
        headers = {'content-type': 'application/json'}
        if data:
            print data
            r = requests.request(method, url, data=data, headers=headers, timeout=30.0)
        else:
            r = requests.request(method, url, headers=headers, timeout=30.0)

        #r = requests.request(method, url, data=data, headers=headers, timeout=30.0)
        if 2 != r.status_code/100:
            raise AssertionError('{method} "{url}" responded with "{code}" status code'
                                    .format(method=method.upper(), url=url, code=r.status_code))
        return r.json()

    def __getattr__(self, item):
        getters = ['testsets', 'tests', 'testruns']
        if item in getters:
            url = ''.join([self.url, '/', item])
            return lambda: self._request('GET', url)

    def testruns_last(self, cluster_id):
        url = ''.join([self.url, '/testruns/last/',
                       str(cluster_id)])
        return self._request('GET', url)

    def start_testrun(self, testset, cluster_id):
        return self.start_testrun_tests(testset, [], cluster_id)

    def start_testrun_tests(self, testset, tests, cluster_id):
        url = ''.join([self.url, '/testruns'])
        data = [{'testset': testset,
                 'tests': tests,
                 'metadata': {'cluster_id': str(cluster_id)}}]
        return self._request('POST', url, data=dumps(data))

    def stop_testrun(self, testrun_id):
        url = ''.join([self.url, '/testruns'])
        data = [{"id": testrun_id,
                 "status": "stopped"}]
        return self._request("PUT", url, data=dumps(data))

    def stop_testrun_last(self, testset, cluster_id):
        latest = self.testruns_last(cluster_id)
        testrun_id = [item['id'] for item in latest if item['testset'] == testset][0]
        return self.stop_testrun(testrun_id)

    def restart_tests(self, tests, testrun_id):
        url = ''.join([self.url, '/testruns'])
        body = [{'id': str(testrun_id),
                 'tests': tests,
                 'status': 'restarted'}]
        return self._request('PUT', url, data=dumps(body))

    def restart_tests_last(self, testset, tests, cluster_id):
        latest = self.testruns_last(cluster_id)
        testrun_id = [item['id'] for item in latest if item['testset'] == testset][0]
        return self.restart_tests(tests, testrun_id)

    def run_and_timeout_unless_finished(self, action, testset, tests, cluster_id, timeout):

        if action == 'run':
            action = lambda: self.start_testrun_tests(testset, tests, cluster_id)
        elif action == 'restart':
            action = lambda: self.restart_tests_last(testset, tests, cluster_id)
        else:
            raise KeyError('Not Appropriate action')
        current_status = None
        current_failed_tests_statuses = None

        start_time = time.time()

        json = action()

        if json == [{}]:
            self.stop_testrun_last(testset, cluster_id)
            time.sleep(1)
            action()

        while time.time() - start_time <= timeout:
            time.sleep(5)

            current_response = self.testruns_last(cluster_id)

            current_testset = [item for item in current_response
                               if item.get('testset') == testset][0]
            current_status = current_testset['status']
            current_failed_tests_statuses = {item['id']: [item['status'], item['message']]
                                             for item in current_testset['tests'] if item['status'] != 'success'}

            if current_status == "finished":
                return {'status': 'finished',
                        'tests': current_failed_tests_statuses}

        self.stop_testrun_last(testset, cluster_id)

        return {'status': current_status,
                'tests': current_failed_tests_statuses}



