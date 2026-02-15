import os
from redis import Redis
from rq import Queue


def get_redis_url():
    return os.getenv("REDIS_URL")


def get_sync_queue():
    redis_url = get_redis_url()
    if not redis_url:
        return None
    return Queue("manufacturer-sync", connection=Redis.from_url(redis_url), default_timeout=3600)
