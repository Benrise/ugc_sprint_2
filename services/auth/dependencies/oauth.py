from functools import lru_cache

from db.postgres import get_session
from dependencies.user import get_user_service
from fastapi import Depends
from services.oauth import OAuthService
from services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession


@lru_cache()
def get_oauth_service(db_session: AsyncSession = Depends(get_session),
                      user_service: UserService = Depends(get_user_service)) -> OAuthService:
    return OAuthService(db_session=db_session, user_service=user_service)
