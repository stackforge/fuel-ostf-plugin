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

__author__ = 'ekonstantinov'
import requests
from json import dumps
import time


class TestingAdapterClient(object):
    def __init__(self, url):
        self.url = url

    def _request(self, method, url, data=None):
        headers = {'content-type': 'application/json'}
        if data:
            r = requests.request(method, url, data=data, headers=headers)
        else:
            r = requests.request(method, url, headers=headers)
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
        url = ''.join([self.url, '/testruns/last/', str(cluster_id)])
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
        data = [{"id": testrun_id, "status": "stopped"}]
        return self._request("PUT", url, data=dumps(data))

    def stop_testrun_last(self, cluster_id, testset):
        latest = self.testruns_last(cluster_id)
        testrun_id = [item['id'] for item in latest if item['testset'] == testset][0]
        return self.stop_testrun(testrun_id)

    def restart_tests(self, cluster_id, tests):
        url = ''.join([self.url, '/testruns'])
        body = [{'id': str(cluster_id), 'tests': tests,
                'status': 'restarted'}]
        return self._request('PUT', url, data=dumps(body))




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


    def run_test_set_and_wait_for_finished(self, testset, config, cluster_id, timeout):

        state = "finished"
        def state_finder(submitie):
            status = [y['status'] for y in submitie if y['testset'] == 'fuel_sanity']
            return status[0] if status else None

        event = lambda: self.start_testrun(testset, config, cluster_id)
        stop_sequence = lambda: self.start_testrun()"""