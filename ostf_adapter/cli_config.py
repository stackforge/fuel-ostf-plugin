from oslo.config import cfg



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
    cfg.StrOpt('dp_path',
               metavar='DB_PATH',
               default=
               'postgresql+psycopg2://adapter:demo@localhost/testing_adapter',
               help='Database connection string',
               ),
    cfg.StrOpt('nailgun-host',
               default='127.0.0.1'),
    cfg.StrOpt('nailgun-port',
               default='3232')
]

cfg.CONF.register_cli_opts(cli_opts)

cfg.CONF(project='testing_adapter')