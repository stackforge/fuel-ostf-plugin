__author__ = 'ekonstantinov'
import requests
from json import dumps


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

    def start_testrun(self, testset, config, cluster_id):
        url = ''.join([self.url, '/testruns'])
        data = [{'testset': testset,
                'metadata': {'config': config,
                'cluster_id': cluster_id}}]
        return self._request('POST', url, data=dumps(data))

    def stop_testrun(self, testrun_id):
        url = ''.join([self.url, '/testruns'])
        data = [{"id": testrun_id, "status": "stopped"}]
        return self._request("PUT", url, data=dumps(data))