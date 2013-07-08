__author__ = 'ekonstantinov'
import requests


class TestingAdapterClient(object):
    def __init__(self, url):
        self.url = url

    def _request(self, method, url, data=None):
        headers = {'content-type': 'application/json'}
        r = requests.request(method, url, data=data, headers=headers)
        if 2 != r.status_code/100:
            raise AssertionError('{url} responded with {code}'.format(usrl=url, code=r.status_code))
        return r.json()

    def __getattr__(self, item):
        getters = ['testsets', 'tests', 'testruns']
        if item in getters:
            url = ''.join([self.url, '/', item])
            return lambda: self._request('GET', url)

    def testruns_last(self, cluster_id):
        url = ''.join([self.url, '/testruns/', cluster_id])
        return self._request('GET', url)

    def start_testrun(self, testset, metadata):
        url = ''.join([self.url, '/testruns'])
        data = {"testset": testset, "metadata": metadata}
        return self._request('POST', url, data=data)

    def stop_testrun(self, testrun_id):
        url = ''.join([self.url, '/testruns'])
        data = {"id": testrun_id, "status": "stopped"}
        self._request("PUT", url, data=data)