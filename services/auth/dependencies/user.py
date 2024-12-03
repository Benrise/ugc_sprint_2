from functools import lru_cache

from db.redis import get_redis
from fastapi import Depends
from redis.asyncio import Redis
from services.user import UserService


@lru_cache()
def get_user_service(cache: Redis = Depends(get_redis)) -> UserService:
    return UserService(cache)
