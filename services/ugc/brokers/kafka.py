from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from utils.abstract import AsyncMessageBroker


class KafkaAdapter(AsyncMessageBroker):
    def __init__(self, producer: AIOKafkaProducer, consumer: AIOKafkaConsumer):
        self.producer = producer
        self.consumer = consumer

    async def produce(self, topic: str, key: str, value: str, **kwargs):
        await self.producer.send_and_wait(topic, key=key.encode(), value=value.encode(), **kwargs)

    async def consume(self, topic: str, group_id: str, **kwargs):
        self.consumer.subscribe([topic])
        async for message in self.consumer:
            yield {
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "key": message.key.decode() if message.key else None,
                "value": message.value.decode(),
            }
