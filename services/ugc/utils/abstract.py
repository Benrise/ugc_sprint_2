from abc import ABC, abstractmethod


class AsyncMessageBroker(ABC):
    @abstractmethod
    async def produce(self, topic: str, key: str, value: str, **kwargs):
        """Отправить сообщение в Kafka"""
        pass

    @abstractmethod
    async def consume(self, topic: str, group_id: str, **kwargs):
        """Читать сообщения из Kafka"""
        pass
