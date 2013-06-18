from core.storage import redis_storage, sql_storage
from oslo.config import cfg

STORAGE_OPTS = [
    cfg.StrOpt('database_connection',
               default='sqlite://',
               help='Database connection string',
               ),
]

cfg.CONF.register_opts(STORAGE_OPTS)


def get_storage():
    return sql_storage.SqlStorage(cfg.CONF.database_connection)