from core.transport import jenkins_adapter, nose_adapter
from oslo.config import cfg

plugins = cfg.ListOpt('plugins', default=[],
                      help='plugins mapping that will be used for custom test running')

cfg.CONF.register_opt(plugins)


def get_transport(service_name):
    for plugin in cfg.CONF.plugins:
        test_run, plug = plugin.split('=')
        if test_run == service_name:
            return nose_adapter.NoseDriver()