from core.storage import redis_storage, sql_storage
from oslo.config import cfg

CONF = cfg.CONF

STORAGE_OPTS = [
    cfg.StrOpt('database_connection',
               default='sqlite://',
               help='Database connection string',
               ),
]

CONF.register_opts(STORAGE_OPTS)




def get_storage():
    print cfg.CONF.database_connection
    return sql_storage.SqlStorage(cfg.CONF.database_connection)