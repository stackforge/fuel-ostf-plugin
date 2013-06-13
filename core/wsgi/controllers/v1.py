from pecan import rest, expose, request, response
import json


class V1Controller(rest.RestController):

    @expose('json')
    def post(self, test_service):
        conf = json.loads(request.body)
        return request.api.run(test_service, conf)

    @expose('json')
    def get(self, test_run, test_run_id=1, test_id=None, stats=False):
        return request.api.get_info(test_run, test_run_id, test_id, stats)

    @expose('json')
    def delete(self):
        request.api.flush_storage()
        return {}