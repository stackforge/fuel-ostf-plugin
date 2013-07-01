from ostf_adapter.storage import sql_storage
from oslo.config import cfg
import logging

log = logging.getLogger(__name__)

CONF = cfg.CONF


def get_storage():
    log.info('GET STORAGE FOR - %s' % cfg.CONF.dp_path)
    return sql_storage.SqlStorage(cfg.CONF.dp_path)