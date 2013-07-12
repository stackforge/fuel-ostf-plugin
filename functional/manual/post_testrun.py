import gevent
from gevent import monkey
monkey.patch_all()
import requests
import json
import time

import pprint

def make_requests(claster_id, test_set):
    body = [{'testset': test_set,
    'metadata': {'config': {},
                'cluster_id': claster_id}}]
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://172.18.164.133:8777/v1/testruns',
                             data=json.dumps(body), headers=headers)
    pprint.pprint(response.json())


if __name__ == '__main__':
    make_requests(21, 'fuel_sanity')