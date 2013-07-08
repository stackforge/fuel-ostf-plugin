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
	_id = response.json()[0]['id']
	time.sleep(1)
	body = [{'id': _id, 'status': 'stopped'}]
	update = requests.put('http://localhost:8989/v1/testruns', data=json.dumps(body), headers=headers)
	get_resp = requests.get('http://localhost:8989/v1/testruns/last/%s' % claster_id)
	data = get_resp.json()
	pprint.pprint(data)

if __name__ == '__main__':
	make_requests(11, 'plugin_stopped')