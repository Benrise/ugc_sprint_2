from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from utils.abstract import AsyncCacheStorage

redis: Redis | None = Redis(host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True)


class RedisCacheAdapter(AsyncCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int):
        await self.redis.set(key, value, expire)


async def get_redis() -> Redis:
    return redis


async def get_cache(redis: Redis = Depends(get_redis)) -> AsyncCacheStorage:
    return RedisCacheAdapter(redis)
