import pecan
from ostf_adapter import api


class APIHook(pecan.hooks.PecanHook):


    def before(self, state):
        state.request.api = api.API()
