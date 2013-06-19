import sys
import os
import logging
from logging.config import dictConfig

from oslo.config import cfg


_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging_opts = [
    cfg.StrOpt('log_file',
               default='testing-adapter.log',
               metavar='PATH',
               deprecated_name='logfile',
               help='(Optional) Name of log file to output to. '
                    'If not set, logging will go to stdout.'),
    cfg.StrOpt('log_dir',
               default='.',
               deprecated_name='logdir',
               help='(Optional) The directory to keep log files in '
                    '(will be prepended to --log-file)'),
    cfg.StrOpt('log_format',
               default=_DEFAULT_LOG_FORMAT,
               metavar='FORMAT',
               help='A logging.Formatter log message format string which may '
                    'use any of the available logging.LogRecord attributes. '
                    'Default: %(default)s'),
    cfg.StrOpt('log_date_format',
               default=_DEFAULT_LOG_DATE_FORMAT,
               metavar='DATE_FORMAT',
               help='Format string for %%(asctime)s in log records. '
                    'Default: %(default)s'),
]


CONF = cfg.CONF
CONF.register_opts(logging_opts)


def get_logger_path():
    dir_path = os.path.abspath(CONF.log_dir)
    return os.path.join(dir_path, CONF.log_file)

logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['streamlog', 'filelog']
    },
    'loggers': {
        'adapter': {
            'level': 'DEBUG',
            'handlers': ['streamlog'],
            'propagate': True
        },
    },
    'handlers': {
        'streamlog': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'filelog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': get_logger_path(),
        },
    },
    'formatters': {
        'verbose': {
            'format': _DEFAULT_LOG_FORMAT,
            'date_format': _DEFAULT_LOG_DATE_FORMAT,
        }
    },
}


def setup():
    dictConfig(logging_config)



