from core.transport import jenkins_adapter, nose_adapter
from oslo.config import cfg
from stevedore import driver
import logging

plugins = cfg.ListOpt('plugins', default=[],
                      help='plugins mapping that will be used for custom test running')

cfg.CONF.register_opt(plugins)

log = logging.getLogger(__name__)

PLUGINS_NAMESPACE = 'plugins'


def get_transport(service_name):
    log.info('GET TRANSPORT FOR - %s' % service_name)
    # TODO remove nose hardcode from driver manager
    mgr = driver.DriverManager(PLUGINS_NAMESPACE,
                               'nose',
                               invoke_on_load=True)
    return mgr.driver