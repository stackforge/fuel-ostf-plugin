import os
import sys
from alembic import command, config, util
from oslo.config import cfg


def do_apply_migrations():
    conf = config.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini')
    )
    conf.set_main_option('script_location', 'ostf_adapter.storage.sql:migrations')
    conf.set_main_option('sqlalchemy.url', cfg.CONF.dbpath)
    getattr(command, 'upgrade')(conf, 'head')