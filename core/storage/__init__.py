from core.storage import redis_storage, sql_storage


def get_storage():
    return sql_storage.SqlStorage('postgresql+psycopg2://postgres:demo@localhost/testing_adapter')