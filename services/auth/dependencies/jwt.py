from functools import lru_cache

from db.redis import get_redis
from fastapi import Depends
from redis.asyncio import Redis
from schemas.auth_request import AuthRequest
from services.jwt import JWTBearer, JWTService
from sqlalchemy.ext.asyncio import AsyncSession


@lru_cache()
def get_jwt_service(cache: Redis = Depends(get_redis)) -> JWTService:
    return JWTService(cache)


async def get_current_user_global(request: AuthRequest, user: AsyncSession = Depends(JWTBearer())):
    request.custom_user = user
