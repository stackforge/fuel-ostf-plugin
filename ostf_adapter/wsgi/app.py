import pecan
from oslo.config import cfg
from ostf_adapter.wsgi import hooks

CONF = cfg.CONF

pecan_config_dict = {
    'app': {
        'root': 'ostf_adapter.wsgi.controllers.root.RootController',
        'modules': ['ostf_adapter.wsgi'],
        'debug': False,
    }
}


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [hooks.ExceptionHandlingHook()]
    if pecan_config:
        pecan_config_dict.update(pecan_config)
    pecan_config = pecan.configuration.conf_from_dict(pecan_config_dict)

    app = pecan.make_app(
        pecan_config.app.root,
        debug=getattr(pecan_config.app, 'debug', False),
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks
    )
    return app

