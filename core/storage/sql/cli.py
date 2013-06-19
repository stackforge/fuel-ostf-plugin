import os
import sys
from alembic import command, config, util
from oslo.config import cfg


STORAGE_OPTS = [
    cfg.StrOpt('database_connection',
               default='sqlite://',
               help='Database connection string',
               ),
]

CONF = cfg.ConfigOpts()

CONF.register_opts(STORAGE_OPTS)


def do_alembic_command(config, cmd, *args, **kwargs):
    try:
        getattr(command, cmd)(config, *args, **kwargs)
    except util.CommandError, e:
        util.err(str(e))


def do_upgrade_downgrade(config, cmd):
    if not CONF.command.revision and not CONF.command.delta:
        raise SystemExit('You must provide a revision or relative delta')


    if CONF.command.delta:
        sign = '+' if CONF.command.name == 'upgrade' else '-'
        revision = sign + str(CONF.command.delta)
    else:
        revision = CONF.command.revision

    do_alembic_command(config, cmd, revision, sql=CONF.command.sql)


def add_command_parsers(subparsers):
    for name in ['upgrade', 'downgrade']:
        parser = subparsers.add_parser(name)
        parser.add_argument('--delta', type=int)
        parser.add_argument('--sql', action='store_true')
        parser.add_argument('revision', nargs='?')
        parser.set_defaults(func=do_upgrade_downgrade)


command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help='Available commands',
                                handler=add_command_parsers)


CONF.register_cli_opt(command_opt)


def main():
    conf = config.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini')
    )
    CONF()
    conf.set_main_option('script_location', 'core.storage.sql:migrations')
    conf.set_main_option('sqlalchemy.url', CONF.database_connection)
    CONF.command.func(conf, CONF.command.name)