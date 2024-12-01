from fastapi import HTTPException, Depends
from http import HTTPStatus
from functools import wraps, lru_cache

from services.role import RoleService
from schemas.user import UserInDBRole, UserRoles
from db.redis import get_redis
from redis.asyncio import Redis


def roles_required(roles_list: list[UserRoles]):
    def decorator(fuction):
        @wraps(fuction)
        async def wrapper(*args, **kwargs):
            user: UserInDBRole = kwargs.get('request').custom_user
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
