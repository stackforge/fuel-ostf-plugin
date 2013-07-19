import pecan
from ostf_adapter.wsgi import hooks


pecan_config_dict = {
    'server': {
        'host': '0.0.0.0',
        'port': 8989
    },
    'app': {
        'root': 'ostf_adapter.wsgi.controllers.root.RootController',
        'modules': ['ostf_adapter.wsgi'],
        'debug': False,
    },
    'nailgun': {
        'host': '127.0.0.1',
        'port': 8000
    }
}


def setup_config(pecan_config=None):
    if pecan_config:
        pecan_config_dict.update(pecan_config)
    pecan.conf.update(pecan_config_dict)


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [hooks.ExceptionHandlingHook()]
    app = pecan.make_app(
        pecan.conf.app.root,
        debug=False,
        force_canonical=True,
        hooks=app_hooks
    )
    return app

