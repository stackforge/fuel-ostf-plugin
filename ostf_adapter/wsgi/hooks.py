from pecan import hooks, response
from ostf_adapter import api
import logging

log = logging.getLogger(__name__)

class ExceptionHandlingHook(hooks.PecanHook):


    def on_error(self, state, e):
    	log.exception('Got an %s.' % e)
