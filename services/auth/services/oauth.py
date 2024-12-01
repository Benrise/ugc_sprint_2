import uuid
from fastapi import HTTPException, Request
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import OAuthYandexSettings
from models.entity import OAuth2User, User
from schemas.user import OAuthData
from utils.abstract import OAuthProvider
from utils.generators import generate_unique_login
from utils.logger import logger
from services.user import UserService


class YandexOAuthProvider(OAuthProvider):
    def __init__(self, client):
        super().__init__(client, 'yandex')

    async def process_token(self, token) -> OAuthData:
        res = (await self.client.get('info', token=token)).json()
        user_id = res['id']
        user_email = res['default_email']
        return OAuthData(user_id=user_id, email=user_email)


class OAuthProviderFactory:
    @staticmethod
    def create_provider(name, client):
        if name == 'yandex':
            return YandexOAuthProvider(client)
        else:
            raise ValueError("Unsupported provider")


class OAuthService:
    def __init__(self, db_session: AsyncSession, user_service: UserService):
        self.db = db_session
        self.user_service = user_service
        self.oauth = OAuth()
        self.yandex_config = OAuthYandexSettings()
        self.providers = {}
        self._register_providers()

    def _register_providers(self):
        self.oauth.register(
            name='yandex',
            client_id=self.yandex_config.client_id,
            client_secret=self.yandex_config.client_secret,
            authorize_url=self.yandex_config.authorize_url,
            access_token_url=self.yandex_config.access_token_url,
            redirect_uri=self.yandex_config.redirect_uri,
            api_base_url=self.yandex_config.api_base_url,
            client_kwargs={'scope': self.yandex_config.scope},
        )

    async def get_provider(self, name) -> OAuthProvider | None:
        if name not in self.providers:
            client = self.oauth.create_client(name)
            provider = OAuthProviderFactory.create_provider(name, client)
            self.providers[name] = provider
        return self.providers[name]

    async def redirect(self, request: Request, provider: str) -> RedirectResponse:
        try:
            client = await self.get_provider(provider)
            if not client:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Wrong oauth provider.")
        except Exception as e:
            logger.error(f"Error getting OAuth provider: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error getting OAuth provider")

        try:
            return await client.redirect(request)
        except Exception as e:
            logger.error(f"Error during redirect to OAuth provider: {e}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="OAuth redirect failed")

    async def authenticate(self, request, provider: str, authorize: AuthJWT, db: AsyncSession) -> [str, str, User]:
        client = await self.get_provider(provider)
        try:
            token = await client.authorize_access_token(request)
        except OAuthError as error:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"{error}")
        user_data = await client.process_token(token)

        oauth_user = await self.db.scalar(
            select(OAuth2User).where(OAuth2User.oauth_id == user_data.user_id,
                                     OAuth2User.provider == provider)
        )

        if oauth_user:
            user = await self.db.get(User, oauth_user.user_id)
        else:
            try:
                login = generate_unique_login()
                user = User(login=login,
                            password=str(uuid.uuid4()),
                            email=user_data.email,
                            is_oauth2=True,
                            credentials_updated=False)
                self.db.add(user)
                await self.db.flush()
                oauth_user = OAuth2User(oauth_id=user_data.user_id, provider=provider, user_id=user.id)
                self.db.add(oauth_user)
                await self.db.commit()
            except SQLAlchemyError as e:
                logger.error(f"Database error during user creation: {e}")
                await self.db.rollback()
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="User creation failed")

        return await self.user_service.complete_oauth2_authentication(user, request, authorize, db)
