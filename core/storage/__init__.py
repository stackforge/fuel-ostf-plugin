from core.storage import redis_storage


def get_storage():
    return redis_storage.RedisStorage()