import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    clickhouse_protocol: str = Field('http', alias='CLICKHOUSE_SERVICE_PROTOCOL')
    clickhouse_host: str = Field('clickhouse', alias='CLICKHOUSE_SERVICE_HOST')
    clickhouse_port: int = Field(8123, alias='CLICKHOUSE_SERVICE_PORT')
    kafka_bootstrap_servers: str = Field(..., alias='UGC_KAFKA_BOOTSTRAP_SERVERS')
    kafka_topics: list = [
        "movie_progress-events",
        "movie_filters-events",
        "movie_details-events",
    ]
    etl_batch_size: int = Field(100, alias='UGC_ETL_BATCH_SIZE')
    kafka_consume_timeout_seconds: int = Field(10, alias='UGC_ETL_KAFKA_CONSUME_TIMEOUT_SECONDS')
    kafka_consume_max_records: int = Field(1000, alias='UGC_ETL_KAFKA_CONSUME_MAX_RECORDS')

    @property
    def clickhouse_url(self) -> str:
        url = f"{self.clickhouse_protocol}://{self.clickhouse_host}:{self.clickhouse_port}"
        return url


settings = Settings()
