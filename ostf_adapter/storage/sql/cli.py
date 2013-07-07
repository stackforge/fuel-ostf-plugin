import os
import sys
from alembic import command, config, util
from pecan import conf

def do_apply_migrations():
    conf = config.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini')
    )
    conf.set_main_option('script_location', 'ostf_adapter.storage.sql:migrations')
    conf.set_main_option('sqlalchemy.url', conf.dbpath)
    getattr(command, 'upgrade')(conf, 'head')