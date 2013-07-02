from pecan import rest, expose, request, response
from pecan.core import abort
import simplejson as json
from ostf_adapter.api import API, parse_json_file
import logging
from ostf_adapter import exceptions as exc


log = logging.getLogger(__name__)


V1_DESCRIPTION = 'data/v1_description.json'


class V1Controller(rest.RestController):

    def __init__(self, *args, **kwargs):
        self.api = API()
        self._api_description = parse_json_file(V1_DESCRIPTION)
        super(V1Controller, self).__init__(*args, **kwargs)

    @expose('json')
    def _default(self):
        return self._api_description

    @expose('json')
    def post(self, test_service):
        if request.body:
            conf = json.loads(request.body)
        else:
            conf = {}
        log.info('POST REQUEST - %s\n'
                 'WITH CONF - %s' %(test_service, conf))
        try:
            return self.api.run(test_service, conf)
        except exc.OstfException, e:
            response.status = e.code
            return {'message': e.message}


    @expose('json')
    def get_all(self):
        return self.api.commands

    @expose('json')
    def get(self, test_run, test_run_id=None):
        log.info('GET REQUEST - %s - %s' % (test_run, test_run_id))
        if not test_run_id:
            response.status = 400
            return {'message': 'Please provide ID of test run'}
        try:
            return self.api.get_info(test_run, test_run_id)
        except exc.OstfException, e:
            response.status = e.code
            return {'message': e.message}

    @expose('json')
    def delete(self, test_run, test_run_id=None):
        log.info('KILL REQUEST - %s - %s' % (test_run, test_run_id))
        if not test_run_id:
            response.status = 400
            return {'message': 'Please provide ID of test run'}
        try:
            result = self.api.kill(test_run, test_run_id)
        except exc.OstfException, e:
            response.status = e.code
            return {'message': e.message}
        if result:
            return {'message': 'Killed test run with ID %s' % test_run_id}
        return {'message': 'Test run %s already finished' % test_run_id}

    def _handle_post(self, method, remainder):
        if not remainder or remainder == ['']:
            controller = self._find_controller('_default')
            if controller:
                return controller, []
        return super(V1Controller, self)._handle_post(method, remainder)

    
