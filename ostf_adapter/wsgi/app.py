import pecan
from ostf_adapter.wsgi import hooks


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
    pecan.conf.update(pecan_config_dict)
    app = pecan.make_app(
        pecan.conf.app.root,
        debug=False,
        force_canonical=True,
        hooks=app_hooks
    )
    
    return app

