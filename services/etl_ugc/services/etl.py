from typing import Any, Dict, List

from aiokafka import AIOKafkaConsumer
from core.config import settings
from db.clickhouse import ClickHouseAdapter
from schemas.events import MovieDetailsEvent, MovieFiltersEvent, MovieProgressEvent
from utils.logger import logger
from utils.sql_queries import MOVIE_DETAILS_QUERY, MOVIE_FILTERS_QUERY, MOVIE_PROGRESS_QUERY


class ETLService:
    def __init__(self, clickhouse_service: ClickHouseAdapter, kafka_servers: str, kafka_topics: List[str], batch_size: int):
        self.clickhouse_service = clickhouse_service
        self.kafka_servers = kafka_servers
        self.kafka_topics = kafka_topics
        self.batch_size = batch_size
        self.consumer = None
        self.batch = []

    async def start(self):
        """Запуск ETL-сервиса."""
        await self.clickhouse_service.init()
        await self.consume_kafka()

    async def consume_kafka(self):
        """Настройка и запуск Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            *self.kafka_topics,
            bootstrap_servers=self.kafka_servers,
            group_id="etl_ugc",
            enable_auto_commit=False,
        )
        await self.consumer.start()
        try:
            logger.info("Kafka consumer started")
            while True:
                messages = await self.consumer.getmany(
                    timeout_ms=settings.kafka_consume_timeout_seconds * 1000,
                    max_records=settings.kafka_consume_max_records
                )
                for topic_partition, messages_list in messages.items():
                    logger.info(f"Got {len(messages)} messages from topic {topic_partition.topic}")
                    topic = topic_partition.topic
                    for message in messages_list:
                        logger.info(f"Received message: {message.value}")
                        event = self.parse_event(topic, message.value)
                        self.batch.append(event)
                        logger.info(f"Added message to batch. Size of batch after adding: {len(self.batch)}")

                        if len(self.batch) >= self.batch_size:
                            await self.process_batch(self.batch)
                            self.batch = []

                    await self.consumer.commit()
        finally:
            await self.consumer.stop()

    def parse_event(self, topic: str, message: bytes) -> Dict[str, Any]:
        """Парсинг и валидация событий в зависимости от топика."""

        message_str = message.decode("utf-8")

        if topic == "movie_progress-events":
            return MovieProgressEvent.model_validate_json(message_str)
        elif topic == "movie_filters-events":
            return MovieFiltersEvent.model_validate_json(message_str)
        elif topic == "movie_details-events":
            return MovieDetailsEvent.model_validate_json(message_str)
        else:
            raise ValueError(f"Unknown topic: {topic}")

    async def process_batch(self, batch: List[Dict[str, Any]]):
        """Обработка батча событий и отправка их в ClickHouse."""
        logger.info(f"Processing batch of {len(batch)} events")

        progress_events = [event.as_tuple() for event in batch if isinstance(event, MovieProgressEvent)]
        filters_events = [event.as_tuple() for event in batch if isinstance(event, MovieFiltersEvent)]
        details_events = [event.as_tuple() for event in batch if isinstance(event, MovieDetailsEvent)]

        if progress_events:
            await self.clickhouse_service.execute(
                MOVIE_PROGRESS_QUERY["insert_data"],
                *progress_events
            )
        if filters_events:
            await self.clickhouse_service.execute(
                MOVIE_FILTERS_QUERY["insert_data"],
                *filters_events
            )
        if details_events:
            await self.clickhouse_service.execute(
                MOVIE_DETAILS_QUERY["insert_data"],
                *details_events
            )
