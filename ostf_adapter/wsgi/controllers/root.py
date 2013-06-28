from pecan import expose
from ostf_adapter.wsgi.controllers import v1


class RootController(object):

    v1 = v1.V1Controller()

    @expose('json', generic=True)
    def index(self): 
        return {'versions': {'v1': '/v1/'},
        		'message': 'Use specific version request'}
