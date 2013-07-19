from pecan import rest, expose, request, response
from pecan.core import abort
import json
from ostf_adapter.api import API
import logging
from ostf_adapter import exceptions as exc


log = logging.getLogger(__name__)


class BaseRestController(rest.RestController):

    def _handle_get(self, method, remainder):
        if len(remainder) > 1:
            method_name = '_'.join(remainder[:2])
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    'get_%s' % method_name,
                    method_name
                )
                if controller:
                    return controller, remainder[2:]
        else:
            method_name = remainder[0]
            if method.upper() in self._custom_actions.get(method_name, []):
                controller = self._find_controller(
                    'get_%s' % method_name,
                    method_name
                )
                if controller:
                    return controller, []
        return super(BaseRestController, self)._handle_get(method, remainder)

class V1Controller(BaseRestController):
    """
        TODO Rewrite it with wsme expose
    """

    def __init__(self, *args, **kwargs):
        self.api = API()
        super(V1Controller, self).__init__(*args, **kwargs)

    _custom_actions = {
        'testsets': ['GET'],
        'tests': ['GET'],
        'testruns': ['GET', 'POST', 'PUT'],
        'testruns_last': ['GET']
    }

    @expose('json')
    def index(self):
        return {}

    @expose('json')
    def get_testsets(self):
        return self.api.get_test_sets()

    @expose('json')
    def get_tests(self):
        return self.api.get_tests()

    @expose('json')
    def get_testruns(self, id=None):
        if not id:
            return self.api.get_test_runs()
        return self.api.get_test_run(id)

    @expose('json')
    def get_testruns_last(self, external_id):
        return self.api.get_last_test_run(external_id)

    @expose('json')
    def post_testruns(self):
        test_runs = json.loads(request.body)
        return self.api.run_multiple(test_runs)

    @expose('json')
    def put_testruns(self):
        test_runs = json.loads(request.body)
        return self.api.update_multiple(test_runs)
