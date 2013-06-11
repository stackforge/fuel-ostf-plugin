from core.storage import redis_storage

STORAGE_ENGINE_NAMESPACE = 'core.storage'


def get_storage():
    return redis_storage.RedisStorage()