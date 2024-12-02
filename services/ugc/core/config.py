import os
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings

from core.logger import LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field(..., alias='UGC_PROJECT_NAME')
    service_port: int = Field(8003, alias='UGC_SERVICE_PORT')
    jwt_secret_key: str = Field(..., alias='UGC_JWT_SECRET_KEY')
    jwt_algorithm: str = Field(..., alias='UGC_JWT_ALGORITHM')
    kafka_bootstrap_servers: str = Field(..., alias='UGC_KAFKA_BOOTSTRAP_SERVERS')
    kafka_group_id: str = Field(..., alias='UGC_KAFKA_GROUP_ID')
    debug: bool = Field(True, alias='UGC_DEBUG')
    mongodb_database_name: str = Field(..., alias='UGC_MONGODB_DATABASE_NAME')
    mongodb_host: str = Field(..., alias='UGC_MONGODB_HOST')
    mongodb_port: int = Field(..., alias='UGC_MONGODB_PORT')

    @property
    def mongodb_base_url(self):
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}"


settings = Settings()
