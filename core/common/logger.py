import os
import logging
import logging.handlers

from oslo.config import cfg


_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging_opts = [
    cfg.StrOpt('log_file',
               default='',
               metavar='PATH',
               deprecated_name='logfile',
               help='(Optional) Name of log file to output to. '
                    'If not set, logging will go to stdout.'),
]


CONF = cfg.CONF
CONF.register_opts(logging_opts)


def setup():
    log = logging.getLogger(None)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    log_file = os.path.abspath(CONF.log_file)
    if log_file:
        file_handler = logging.handlers.WatchedFileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        mode = int('0644', 8)
        os.chmod(log_file, mode)
        log.addHandler(file_handler)

    log.setLevel(logging.INFO)



