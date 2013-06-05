from core.storage import redis_storage

STORAGE_ENGINE_NAMESPACE = 'core.storage'


def get_storage(conf):
    return redis_storage.RedisStorage()