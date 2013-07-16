import requests
import json
import time
import pprint

def make_requests(claster_id, test_set):
    body = [{'id': claster_id, 'status': 'stopped'}]
    headers = {'Content-Type': 'application/json'}
    update = requests.put(
            'http://localhost:8989/v1/testruns',
            data=json.dumps(body), headers=headers)
    data = update.json()
    pprint.pprint(data)

if __name__ == '__main__':
    make_requests(356, 'plugin_stopped')