import pecan
from core import api


class APIHook(pecan.hooks.PecanHook):

    rest_api = api.API()

    def before(self, state):
        state.request.api = self.rest_api


# class StorageHook(hooks.PecanHook):
#
#     def before(self, state):
#         state.request.storage = get_storage(conf)
#
#
# class TransportHook(hooks.PecanHook):
#
#     def before(self, state):
#         state.request.transport = get_transport(conf)

