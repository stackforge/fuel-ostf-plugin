import requests
import json
import time

import pprint

def make_requests(claster_id, test_set):
    tests = ['fuel_health.tests.sanity.test_sanity_networking.NetworksTest.test_list_ports']
    body = [{'id': claster_id,
             'tests': tests,
             'status': 'restarted',
                }]
    headers = {'Content-Type': 'application/json'}
    response = requests.put('http://127.0.0.1:8989/v1/testruns',
                             data=json.dumps(body), headers=headers)
    pprint.pprint(response.json())


if __name__ == '__main__':
    make_requests('336', 'fuel_sanity')