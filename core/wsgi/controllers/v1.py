from pecan import rest, expose, request, response
import json


class V1Controller(rest.RestController):

    @expose('json')
    def post(self, test_service):
        if request.body:
            conf = json.loads(request.body)
        else:
            conf = {}
        return request.api.run(test_service, conf)

    @expose('json')
    def get(self, test_run, test_run_id=1, test_id=None, stats=False):
        return request.api.get_info(test_run, test_run_id, test_id, stats)

    @expose('json')
    def delete(self, test_run, test_run_id=0):
        request.api.kill(test_run, test_run_id)
        return {}