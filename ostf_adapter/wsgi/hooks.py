import pecan
from ostf_adapter import api


class APIHook(pecan.hooks.PecanHook):

    rest_api = api.API()

    def before(self, state):
        state.request.api = self.rest_api
