from functools import lru_cache
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from services.user import UserService
from services.oauth import OAuthService
from dependencies.user import get_user_service


@lru_cache()
def get_oauth_service(db_session: AsyncSession = Depends(get_session),
                      user_service: UserService = Depends(get_user_service)) -> OAuthService:
    return OAuthService(db_session=db_session, user_service=user_service)
