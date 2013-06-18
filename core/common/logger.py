import logging
import logging.config


from oslo.config import cfg



_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


logging_cli_opts = [
    cfg.StrOpt('log-file',
               metavar='PATH',
               deprecated_name='logfile',
               help='(Optional) Name of log file to output to. '
                    'If not set, logging will go to stdout.'),
]


CONF = cfg.CONF
CONF.register_cli_opts(logging_cli_opts)


logging = {
    'loggers': {
        'root': {'level': 'INFO', 'handlers': ['console']},
        'adapter': {'level': 'DEBUG', 'handlers': ['console']},
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        }
    },
}
