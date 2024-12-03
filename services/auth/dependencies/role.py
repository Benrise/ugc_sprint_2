from functools import lru_cache, wraps
from http import HTTPStatus

from db.redis import get_redis
from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis
from schemas.user import UserInDBRole, UserRoles
from services.role import RoleService


def roles_required(roles_list: list[UserRoles]):
    def decorator(fuction):
        @wraps(fuction)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            user: UserInDBRole = getattr(request, 'custom_user', None)
            if not user:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail='Forbidden. Only authorized user have access'
                )
            if user.role_id not in roles_list:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail='You do not have permission to this action'
                )
            return await fuction(*args, **kwargs)
        return wrapper
    return decorator


@lru_cache()
def get_role_service(cache: Redis = Depends(get_redis)) -> RoleService:
    return RoleService(cache)
