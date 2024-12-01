from abc import ABC, abstractmethod
from typing import Any, Optional


class AnalyticDatabaseService(ABC):
    @abstractmethod
    async def execute(self, key: str, params: Optional[dict] = None) -> Any:
        pass

    @abstractmethod
    async def fetch(self, key: str, params: Optional[dict] = None) -> Any:
        pass

    @abstractmethod
    async def health_check(self) -> Any:
        pass

    @abstractmethod
    async def init(self) -> Any:
        pass
