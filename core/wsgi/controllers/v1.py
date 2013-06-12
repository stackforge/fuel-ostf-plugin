from pecan import rest, expose, request, response


class V1Controller(rest.RestController):

    @expose('json')
    def post(self, test_service, **kwargs):
        return request.api.run(test_service,
            {'test_path': ['/home/dshulyak/projects/ceilometer/tests']})

    @expose('json')
    def get(self, test_service, service_id=1, test_id=None, meta=False):
        return request.api.get_info(test_service, service_id, test_id, meta)

    @expose('json')
    def delete(self):
        request.api.flush_storage()
        return {}