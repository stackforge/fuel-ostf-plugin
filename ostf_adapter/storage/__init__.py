from ostf_adapter.storage import sql_storage
import logging
from pecan import conf

log = logging.getLogger(__name__)


DEFAULT_DBPATH = 'postgresql+psycopg2://adapter:demo@localhost/testing_adapter'

def get_storage(dbpath=None):
    log.info('GET STORAGE FOR - %s' % conf.get('db_path', '') or DEFAULT_DBPATH)
    return sql_storage.SqlStorage(conf.get('db_path', '') or DEFAULT_DBPATH)