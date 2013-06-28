import pecan
from oslo.config import cfg
from ostf_adapter.wsgi import hooks

CONF = cfg.CONF

server_opts = [
    cfg.StrOpt('server_host',
               default='0.0.0.0'),
    cfg.StrOpt('server_port',
               default='8777')
]

CONF.register_opts(server_opts)

pecan_config_dict = {
    'server': {
        'host': CONF.server_host,
        'port': CONF.server_port
    },
    'app': {
        'root': 'ostf_adapter.wsgi.controllers.root.RootController',
        'modules': ['ostf_adapter.wsgi'],
        'debug': False,
    }
}


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [hooks.ExceptionHandlingHook()]
    if not pecan_config:
        pecan_config = pecan.configuration.conf_from_dict(pecan_config_dict)

    app = pecan.make_app(
        pecan_config.app.root,
        debug=getattr(pecan_config.app, 'debug', False),
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks
    )
    return app

