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
    response = requests.post('http://127.0.0.1:8989/v1/testruns',
                             data=json.dumps(body), headers=headers)
    pprint.pprint(response.json())


if __name__ == '__main__':
    make_requests('308', 'plugin_general')