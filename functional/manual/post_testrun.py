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
	response = requests.post('http://localhost:8989/v1/testruns', data=json.dumps(body), headers=headers)
	pprint.pprint(response.json())
	status = 'started'
	while status == 'started':
		time.sleep(5)
		get_resp = requests.get('http://localhost:8989/v1/testruns/last/%s' % claster_id)
		data = get_resp.json()
		status = data['status']
		pprint.pprint(data)

if __name__ == '__main__':
	gevent.joinall([gevent.spawn(make_requests, i, 'plugin_general') for i in xrange(100)])