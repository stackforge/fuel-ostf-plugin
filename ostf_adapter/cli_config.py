from oslo.config import cfg
import argparse
import sys

#TODO remove oslo.config from dependencies
cli_opts = [
    cfg.StrOpt('host',
               default='127.0.0.1'),
    cfg.StrOpt('port',
               default='8989'),
    cfg.StrOpt('log_file',
               default=None,
               metavar='PATH',
               deprecated_name='logfile',
               help='(Optional) Name of log file to output to. '
                    'If not set, logging will go to stdout.'),
    cfg.StrOpt('dbpath',
               metavar='DB_PATH',
               default=
               'postgresql+psycopg2://adapter:demo@localhost/testing_adapter',
               help='Database connection string',
               ),
    cfg.StrOpt('nailgun-host',
               default='127.0.0.1'),
    cfg.StrOpt('nailgun-port',
               default='3232'),
    cfg.BoolOpt('after_init_hook', default=None)
]

cfg.CONF.register_cli_opts(cli_opts)

parser = argparse.ArgumentParser()
parser.add_argument('--after-initialization-environment-hook',
                    action='store_true', dest='after_init_hook')
parser.add_argument('--dbpath', metavar='DB_PATH',
    default='postgresql+psycopg2://adapter:demo@localhost/testing_adapter')
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--port', default='8989')
parser.add_argument('--log_file', default=None, metavar='PATH')
parser.add_argument('--nailgun-host', default='127.0.0.1')
parser.add_argument('--nailgun-port', default='3232')
args = parser.parse_args(sys.argv[1:])

for key, value in args.__dict__.iteritems():
    if bool(value):
        setattr(cfg.CONF, key, value)
