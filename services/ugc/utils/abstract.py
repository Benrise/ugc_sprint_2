from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AsyncMessageBroker(ABC):
    @abstractmethod
    async def produce(self, topic: str, key: str, value: str, **kwargs):
        """Отправить сообщение в Kafka"""

    @abstractmethod
    async def consume(self, topic: str, group_id: str, **kwargs):
        """Читать сообщения из Kafka"""


class AsyncNoSQLDatabaseService(ABC):
    @abstractmethod
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def find_many(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        pass
