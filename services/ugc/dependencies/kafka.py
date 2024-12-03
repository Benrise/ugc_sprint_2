from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from brokers.kafka import KafkaAdapter
from fastapi import Depends
from utils.abstract import AsyncMessageBroker

kafka_producer: AIOKafkaProducer | None = None
kafka_consumer: AIOKafkaConsumer | None = None


async def get_kafka_producer() -> AIOKafkaProducer:
    return kafka_producer


async def get_kafka_consumer() -> AIOKafkaConsumer:
    return kafka_consumer


async def get_kafka_service(
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    consumer: AIOKafkaConsumer = Depends(get_kafka_consumer),
) -> AsyncMessageBroker:
    return KafkaAdapter(producer, consumer)
