import os
import logging
import logging.handlers
from oslo.config import cfg


_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup():
    log = logging.getLogger(None)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    if cfg.CONF.log_file:
        log_file = os.path.abspath(cfg.CONF.log_file)
        file_handler = logging.handlers.WatchedFileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        mode = int('0644', 8)
        os.chmod(log_file, mode)
        log.addHandler(file_handler)

    log.setLevel(logging.INFO)



