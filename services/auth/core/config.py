import os
from datetime import timedelta
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QUERY_DESC = "Поисковая строка"
QUERY_ALIAS = "query"

SORT_ORDER_DESC = "Сортировка. asc - по возрастанию, desc - по убыванию"
SORT_ORDER_ALIAS = "sort_order"

SORT_FIELD_DESC = "Поле для сортировки"
SORT_FIELD_ALIAS = "sort_field"

PAGE_DESC = "Номер страницы"
PAGE_ALIAS = "page"

SIZE_DESC = "Количество элементов на странице"
SIZE_ALIAS = "size"

GENRE_DESC = "Фильтр по жанру фильма"
GENRE_ALIAS = "genre_id"

MAX_PAGE_SIZE = 100
MAX_GENRES_SIZE = 50

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field(..., alias='AUTH_PROJECT_NAME')
    service_port: int = Field(8001, alias='AUTH_SERVICE_PORT')
    redis_host: str = Field('redis', alias='AUTH_REDIS_HOST')
    redis_port: int = Field(6379, alias='AUTH_REDIS_PORT')
    debug: bool = Field(True, alias='AUTH_DEBUG')
    secret_key_session: str = Field(..., alias='AUTH_SECRET_KEY_SESSION')
    enable_tracing: bool = Field(..., alias='AUTH_ENABLE_TRACING')
    tracer_host: str = Field(..., alias='AUTH_TRACER_HOST')
    tracer_port: int = Field(..., alias='AUTH_TRACER_PORT')
    hawk_integration_token: str = Field(..., alias='HAWK_INTEGRATION_TOKEN')


settings = Settings()


class OAuthYandexSettings(BaseSettings):
    client_id: str = Field(..., alias='AUTH_YANDEX_CLIENT_ID')
    client_secret: str = Field(..., alias='AUTH_YANDEX_CLIENT_SECRET')
    scope: str = 'login:email'
    api_base_url: str = 'https://login.yandex.ru/'
    authorize_url: str = 'https://oauth.yandex.ru/authorize'
    access_token_url: str = 'https://oauth.yandex.ru/token'
    redirect_uri: str = Field(..., alias='AUTH_YANDEX_REDIRECT_URI')


oauth_yandex = OAuthYandexSettings()


class PostgresSettings(BaseSettings):
    db: str = Field(..., alias='AUTH_POSTGRES_DB_NAME')
    user: str = Field(..., alias='AUTH_POSTGRES_USER')
    password: str = Field(..., alias='AUTH_POSTGRES_PASSWORD')
    host: str = Field(..., alias='AUTH_POSTGRES_HOST')
    port: int = Field(..., alias='AUTH_POSTGRES_PORT')


pg = PostgresSettings()


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = Field(..., alias='AUTH_JWT_SECRET_KEY')
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    algorithm: str = Field('HS256', alias='AUTH_JWT_ALGORITHM')
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    access_expires_minutes: int = Field(..., alias='AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_expires_days: int = Field(..., alias='AUTH_JWT_REFRESH_TOKEN_EXPIRE_DAYS')

    @property
    def access_expires(self) -> timedelta:
        return timedelta(minutes=self.access_expires_minutes)

    @property
    def refresh_expires(self) -> timedelta:
        return timedelta(days=self.refresh_expires_days)


jwt_settings = JWTSettings()
