import requests
import json
import time

import pprint

def make_requests(claster_id, test_set):
    tests = ['functional.dummy_tests.general_test.Dummy_test.test_long_pass']
    body = [{'id': claster_id,
             'tests': tests,
             'status': 'restarted',
                }]
    headers = {'Content-Type': 'application/json'}
    response = requests.put('http://127.0.0.1:8989/v1/testruns',
                             data=json.dumps(body), headers=headers)
    pprint.pprint(response.json())


if __name__ == '__main__':
    make_requests(370, 'plugin_general')