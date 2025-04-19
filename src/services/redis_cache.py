import json

import redis.asyncio as redis

from src.conf.config import settings


class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        """
        Establishes connection to Redis server.

        :param: None
        :return: None
        """
        if self.redis is None:
            self.redis = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            )

    async def set(self, key: str, value: dict, expire: int = 3600):
        """
        Stores value in Redis with specified key.

        :param key: Key to store the value under
        :param value: Dictionary value to store
        :param expire: Time in seconds until key expires, defaults to 1 hour
        :return: None
        """
        if self.redis:
            await self.redis.set(key, json.dumps(value), ex=expire)

    async def get(self, key: str):
        """
        Retrieves value from Redis by key.

        :param key: Key to look up
        :return: Retrieved value as dictionary if found, None otherwise
        """
        if self.redis:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        return None

    async def delete(self, key: str):
        """
        Deletes value from Redis.

        :param key: Key to delete
        :return: None
        """
        if self.redis:
            await self.redis.delete(key)


redis_cache = RedisCache()
