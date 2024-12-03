from http import HTTPStatus
from typing import List
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from core.config import jwt_settings
from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from models.entity import User, UserHistory
from redis.asyncio import Redis
from schemas.user import ChangePassword, ChangeUsername, LoginHistory, UserCreate, UserInDB, UsernameLogin
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from werkzeug.security import generate_password_hash


class UserService:
    def __init__(self, cache: Redis) -> None:
        self.cache = cache

    async def _add_to_db(self, obj: User | UserHistory, db: AsyncSession) -> object | None:
        try:
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj
        except IntegrityError as e:
            msg = str(e.orig).split("\n")[1][9:]
            raise HTTPException(status_code=HTTPStatus.FOUND, detail=msg)

    async def create_user(self, user_create: UserCreate, db: AsyncSession) -> UserInDB | None:
        user_dto = jsonable_encoder(user_create)
        user = User(**user_dto)
        return await self._add_to_db(user, db)

    async def user_validation(self, credentials: UsernameLogin, db: AsyncSession) -> User | None:
        query = await db.execute(select(User).where(User.login == credentials.username))
        user = query.scalars().first()
        return user

    async def get_user(self, db: AsyncSession, authorize: AuthJWT) -> User | None:
        current_user_id = (await authorize.get_raw_jwt())['sub']
        db_user = await db.execute(select(User).where(User.id == current_user_id))
        return db_user.scalars().first()

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> User | None:
        query = await db.execute(select(User).where(User.id == user_id))
        return query.scalars().first()

    async def change_login(self, login: ChangeUsername, user: User, db: AsyncSession) -> User:
        user.login = login.new_username
        return await self._add_to_db(user, db)

    async def change_password(self, password_data: ChangePassword, user: User, db: AsyncSession) -> User:
        user.password = generate_password_hash(password_data.new_password)
        return await self._add_to_db(user, db)

    async def add_login_to_history(self, user: User, db: AsyncSession) -> UserHistory:
        login_history = LoginHistory(user_id=user.id)
        history_entry = UserHistory(**jsonable_encoder(login_history))
        return await self._add_to_db(history_entry, db)

    async def get_login_history(self, user: User, page: int, size: int, db: AsyncSession) -> List[UserHistory]:
        offset = (page - 1) * size
        query = await db.execute(
            select(UserHistory)
            .where(UserHistory.user_id == user.id)
            .order_by(UserHistory.logged_at)
            .limit(size)
            .offset(offset)
        )
        users: List[UserHistory] = query.scalars().all()
        return users

    async def get_all_users(self, db: AsyncSession) -> List[UserInDB]:
        query = await db.execute(select(User))
        users: List[UserInDB] = query.scalars().all()
        return users

    async def complete_oauth2_authentication(self, user: User, _: Request, authorize: AuthJWT, db: AsyncSession) -> tuple[str, str, User]:
        access_token = await authorize.create_access_token(
            subject=str(user.id),
            expires_time=jwt_settings.access_expires,
            user_claims={"user_id": str(user.id)}
        )
        refresh_token = await authorize.create_refresh_token(
            subject=str(user.id),
            expires_time=jwt_settings.refresh_expires,
            user_claims={"user_id": str(user.id)}
        )

        await self.add_login_to_history(user, db)

        return access_token, refresh_token, user
