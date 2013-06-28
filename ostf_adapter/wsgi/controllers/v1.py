from pecan import rest, expose, request, response
import simplejson as json
import logging
from ostf_adapter.api import API

log = logging.getLogger(__name__)


class V1Controller(rest.RestController):

    def __init__(self, *args, **kwargs):
        self.api = API()
        super(V1Controller, self).__init__(*args, **kwargs)

    @expose('json')
    def post(self, test_service):
        if request.body:
            conf = json.loads(request.body)
        else:
            # response.status = 400
            # return {'message': 'Config is expected'}
            conf = {}
        log.info('POST REQUEST - %s\n'
                 'WITH CONF - %s' %(test_service, conf))
        return self.api.run(test_service, conf)

    @expose('json')
    def get(self, test_run, test_run_id=None):
        log.info('GET REQUEST - %s - %s' % (test_run, test_run_id))
        if not test_run_id:
            response.status = 400
            return {'message': 'Please provide ID of test run'}
        return self.api.get_info(test_run, test_run_id)

    @expose('json')
    def delete(self, test_run, test_run_id=None):
        log.info('KILL REQUEST - %s - %s' % (test_run, test_run_id))
        if not test_run_id:
            response.status = 400
            return {'message': 'Please provide ID of test run'}
        result = self.api.kill(test_run, test_run_id)
        if result:
            return {'message': 'Killed test run with ID %s' % test_run_id}
        return {'message': 'Test run %s already finished' % test_run_id}