import pecan
from core.wsgi import config
from core.wsgi import hooks
from oslo.config import cfg


def get_pecan_config():
    # Set up the pecan configuration
    filename = config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [hooks.APIHook()]
    if not pecan_config:
        pecan_config = get_pecan_config()

    app = pecan.make_app(
        pecan_config.app.root,
        logging=getattr(pecan_config, 'logging', {}),
        debug=getattr(pecan_config.app, 'debug', False),
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks
    )
    return app

