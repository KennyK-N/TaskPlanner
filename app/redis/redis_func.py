import redis
import os
from flask import current_app
from app.util.general_utils import *


class RedisConfig:
    """
    Holds a shared Redis connection pool configured from the environment variables.
    """

    pool = redis.ConnectionPool(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        max_connections=20,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )


def redis_init():
    """
    Creates and returns a Redis client using the shared connection pool.
    Returns:
        redis.Redis: A Redis client instance.
    """
    return redis.Redis(connection_pool=RedisConfig.pool)


def redis_get(key):
    """
    Fetches a value from Redis by key, returning None if missing or on error.
    Args:
        key (str): The Redis key to look up.
    Returns:
        str | None: The cached value, or None if not found or Redis fails.
    """
    redis = current_app.extensions["redis"]

    try:
        value = redis.get(key)

    except Exception as exception:
        print(str(exception))
        value = None

    return value


def redis_invalidate(key, user_id):
    """
    Deletes a specific key and clears all paginate cache entries for the given user.
    Args:
        key (str): The direct record key to delete.
        user_id (int): The user's id used to find and clear their paginate cache keys.
    Returns:
        None
    """
    redis = current_app.extensions["redis"]
    try:
        redis.delete(key)
        pattern = f"{user_id}{REDIS_PAGINATE_KEY_FORMAT}*"
        cursor = 0

        while True:
            cursor, keys = redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                redis.delete(*keys)

            if cursor == 0:
                break

    except Exception as exception:
        print(str(exception))


def redis_set(key, value):
    """
    Stores a value in Redis with a TTL, only if the key does not already exist.
    Args:
        key (str): The Redis key to store under.
        value (str): The value to cache.
    Returns:
        None
    """
    redis = current_app.extensions["redis"]
    try:
        redis.set(key, value, ex=REDIS_TTL_VAL, nx=True)
    except Exception as exception:
        print(str(exception))
