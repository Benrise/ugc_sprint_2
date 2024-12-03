from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from core.config import jwt_settings
from db.postgres import get_session
from dependencies.user import get_user_service
from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from redis.asyncio import Redis
from schemas.user import TokensResponse, UserInDBRole
from services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession


class JWTService:
    def __init__(self, cache: Redis) -> None:
        self.cache = cache

    async def create_user_tokens(self, user_id: UUID, authorize: AuthJWT, ) -> TokensResponse:
        access_token = await authorize.create_access_token(
            subject=str(user_id),
            expires_time=jwt_settings.access_expires,
            user_claims={"user_id": str(user_id)}
        )
        refresh_token = await authorize.create_refresh_token(
            subject=str(user_id),
            expires_time=jwt_settings.refresh_expires,
            user_claims={"user_id": str(user_id)}
        )

        return TokensResponse(access_token=access_token, refresh_token=refresh_token)

    async def revoke_tokens(self, tokens: TokensResponse, authorize: AuthJWT):
        access_jti = (await authorize.get_raw_jwt(encoded_token=tokens.access_token))['jti']
        refresh_jti = (await authorize.get_raw_jwt(encoded_token=tokens.refresh_token))['jti']
        await self.cache.setex(access_jti, jwt_settings.refresh_expires, "true")
        await self.cache.setex(refresh_jti, jwt_settings.refresh_expires, "true")

    async def refresh_token(self, authorize: AuthJWT) -> TokensResponse:
        current_user_id = await authorize.get_jwt_subject()

        new_access_token = await authorize.create_access_token(
            subject=current_user_id,
            expires_time=jwt_settings.access_expires,
            user_claims={"user_id": current_user_id}
        )
        new_refresh_token = await authorize.create_refresh_token(
            subject=current_user_id,
            expires_time=jwt_settings.refresh_expires,
            user_claims={"user_id": current_user_id}
        )

        return TokensResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
            self,
            request: Request,
            user_service: UserService = Depends(get_user_service),
            db: AsyncSession = Depends(get_session)) -> UserInDBRole | None:
        authorize = AuthJWT(req=request)
        await authorize.jwt_optional()
        current_user_id = await authorize.get_jwt_subject()
        if not current_user_id:
            return None
        user = await user_service.get_user(db, authorize)
        return UserInDBRole.from_orm(user)
