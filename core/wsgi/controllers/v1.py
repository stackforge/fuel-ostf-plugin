from pecan import rest, expose, request, response


class V1Controller(rest.RestController):

    @expose('json')
    def post(self, test_service, **kwargs):
        res = request.api.invoke_build(test_service, kwargs.get('job'))
        return res

    @expose()
    def head(self, service, *kwargs):
        pass

    @expose()
    def delete(self, test_service):
        request.api.delete_test_service(test_service)
        response.status = 200
        return {}

    @expose('json')
    def get(self, test_service, **kwargs):
        if 'job' in kwargs:
            res = request.api.get_job_test_results(test_service, kwargs['job'])
        else:
            res = request.api.get_test_results(test_service)
        return res