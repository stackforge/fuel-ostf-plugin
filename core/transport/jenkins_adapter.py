import requests
import json


class JenkinsClient(object):

    def __init__(self, jenkins_url='http://localhost:8080'):
        self._url = jenkins_url

    def create_job(self, job_name, config_path):
        headers = {'content-type': 'text/xml'}
        full_url = '{}/createItem'.format(self._url)
        params = {'name': job_name}
        return requests.post(full_url, data=open(config_path, 'rb').read(),
                             headers=headers, params=params)

    def get_jobs(self):
        full_url = self._url + '/api/json'
        res = requests.get(full_url)
        return json.loads(res.text)

    def get_builds(self, job_name):
        full_url = '{}/job/{}/api/json'.format(self._url, job_name)
        res = requests.get(full_url)
        return json.loads(res.text)['builds']

    def get_test_result(self, job_name, build_number):
        full_url = '{}/job/{}/{}/testReport/api/json'.format(
            self._url, job_name, build_number)
        res = requests.get(full_url)
        return json.loads(res.text)

    def invoke_build(self, job_name):
        full_url = '{}/job/{}/build'.format(self._url, job_name)
        return requests.post(full_url)

    def get_last_build(self, job_name):
        full_url = '{}/job/{}/lastBuild/api/json'.format(self._url, job_name)
        res = requests.post(full_url)
        data = json.loads(res.text)
        return {'status': 'BUILDING' if data['building'] else data['result']}

    def get_last_build_test_result(self, job_name):
        full_url = '{}/job/{}/lastBuild/testReport/api/json'.format(self._url,
                                                                    job_name)
        res = requests.post(full_url)
        if res.status_code == 200:
            data = json.loads(res.text)
            suites = data.pop('suites')
            data.update(suites[0])
            return data
        return {}


