import requests
import json
import time

import pprint

def make_requests(claster_id, test_set):
    tests = ['functional.dummy_tests.general_test.Dummy_test.test_fast_pass',
             'functional.dummy_tests.general_test.Dummy_test.test_fast_error']
    body = [{'testset': test_set,
             'tests': tests,
            'metadata': {
            'cluster_id': claster_id}}]
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://127.0.0.1:8989/v1/testruns',
                             data=json.dumps(body), headers=headers)
    pprint.pprint(response.json())


if __name__ == '__main__':
    make_requests('101', 'plugin_general')