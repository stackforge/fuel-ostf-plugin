from core.transport import jenkins_adapter, nose_adapter
from oslo.config import cfg
from stevedore import driver

plugins = cfg.ListOpt('plugins', default=[],
                      help='plugins mapping that will be used for custom test running')

cfg.CONF.register_opt(plugins)


PLUGINS_NAMESPACE = 'plugins'


def get_transport(service_name):
    mgr = driver.DriverManager(PLUGINS_NAMESPACE,
                               'nose',
                               invoke_on_load=True)
    return mgr.driver