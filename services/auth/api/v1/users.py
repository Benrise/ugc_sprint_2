from http import HTTPStatus
from typing import List

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from core.config import jwt_settings
from db.postgres import get_session
from db.redis import redis
from dependencies.jwt import get_jwt_service
from dependencies.oauth import get_oauth_service
from dependencies.role import roles_required
from dependencies.user import get_user_service
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from models.abstract import PaginatedParams
from schemas.auth_request import AuthRequest
from schemas.user import (
    ChangePassword,
    ChangeUsername,
    TokensResponse,
    UserCreate,
    UserHistoryInDB,
    UserInDB,
    UserInDBRole,
    UsernameLogin,
    UserRoles,
)
from services.jwt import JWTService
from services.oauth import OAuthService
from services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
auth_dep = AuthJWTBearer()


@AuthJWT.load_config
def get_config():
    return jwt_settings


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    entry = await redis.get(jti)
    return entry


@router.get('/', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def get_users(
    *,
    request: AuthRequest,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> List[UserInDBRole]:
    await authorize.jwt_required()
    users: List[UserInDBRole] = await user_service.get_all_users(db)
    return users


@router.post('/signup', response_model=UserInDB, status_code=HTTPStatus.CREATED)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
) -> UserInDB:
    user: UserInDB = await user_service.create_user(user_create, db)
    return user


@router.get('/signin/{provider}')
async def yandex_signin(request: Request,
                        provider: str,
                        oauth_service: OAuthService = Depends(get_oauth_service)) -> RedirectResponse:
    return await oauth_service.redirect(request, provider)


@router.get("/signin/{provider}/callback", response_model=TokensResponse)
async def auth_callback(request: Request,
                        provider: str,
                        db: AsyncSession = Depends(get_session),
                        oauth_service: OAuthService = Depends(get_oauth_service),
                        authorize: AuthJWT = Depends(auth_dep)) -> TokensResponse:
    access_token, refresh_token, _ = await oauth_service.authenticate(
        request,
        provider,
        authorize,
        db
    )
    return TokensResponse(access_token=access_token, refresh_token=refresh_token)


@router.post('/signin', response_model=TokensResponse, status_code=HTTPStatus.OK)
async def login(
    credentials: UsernameLogin,
    user_service: UserService = Depends(get_user_service),
    jwt_service: JWTService = Depends(get_jwt_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> TokensResponse | None:
    user = await user_service.user_validation(credentials, db)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Username doesn\'t exists'
        )
    if not user.check_password(credentials.password):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Incorrect password'
        )
    tokens = await jwt_service.create_user_tokens(user.id, authorize)
    await authorize.set_access_cookies(tokens.access_token)
    await authorize.set_refresh_cookies(tokens.refresh_token)
    await user_service.add_login_to_history(user, db)
    return tokens


@router.post('/signout', status_code=HTTPStatus.OK)
async def logout(
    user_service: UserService = Depends(get_user_service),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()
    await authorize.unset_jwt_cookies()
    return {"detail": "Logged out successfully"}


@router.post('/refresh', status_code=HTTPStatus.OK)
async def refresh(
    authorize: AuthJWT = Depends(auth_dep),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> TokensResponse:
    await authorize.jwt_refresh_token_required()

    tokens = await jwt_service.refresh_token(authorize)

    await authorize.set_access_cookies(tokens.access_token)
    await authorize.set_refresh_cookies(tokens.refresh_token)

    return tokens


@router.patch('/change-username', status_code=HTTPStatus.OK)
async def change_username(
    login: ChangeUsername,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    await user_service.change_login(login, user, db)
    await authorize.unset_jwt_cookies()
    return {"detail": "Username successfully updated"}


@router.patch('/change-password', status_code=HTTPStatus.OK)
async def change_password(
    login: ChangePassword,
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    await user_service.change_password(login, user, db)
    await authorize.unset_jwt_cookies()
    return {"detail": "Password successfully updated"}


@router.get(
    '/login-history',
    response_model=list[UserHistoryInDB],
    status_code=HTTPStatus.OK)
async def login_history(
    pagination: PaginatedParams = Depends(),
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> list[UserHistoryInDB]:
    await authorize.jwt_required()

    user = await user_service.get_user(db, authorize)
    history = await user_service.get_login_history(
        user,
        pagination.page,
        pagination.size, db
    )
    login_history = [UserHistoryInDB(
        id=i.id, user_id=i.user_id, logged_at=i.logged_at
    ) for i in history]
    return login_history


@router.get('/verify', status_code=HTTPStatus.OK)
async def validate_token(
    authorize: AuthJWT = Depends(auth_dep),
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session)
) -> dict:
    try:
        await authorize.jwt_required()
        user = await user_service.get_user(db, authorize)

        return {
            "message": "Token is valid",
            "user": {
                "id": user.id,
                "username": user.login,
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}"
        )
