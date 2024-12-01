from fastapi import Depends
from functools import lru_cache

from redis.asyncio import Redis
from services.user import UserService
from db.redis import get_redis


@lru_cache()
def get_user_service(cache: Redis = Depends(get_redis)) -> UserService:
    return UserService(cache)
