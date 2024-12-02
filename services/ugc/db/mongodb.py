from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Dict, List, Optional

from utils.abstract import AsyncNoSQLDatabaseService

from schemas.bookmark import Bookmark
from schemas.film import FilmRating
from schemas.review import Review, ReviewLike


MongoDocuments = [
    Bookmark,
    FilmRating,
    Review,
    ReviewLike
]


class MongoDBAdapter(AsyncNoSQLDatabaseService):
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.client = client
        self.database = client[database_name]

    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            result = await self.database[collection].find_one(query)
            return result if result is not None else None
        except Exception:
            return None

    async def find_many(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            cursor = self.database[collection].find(query)
            return await cursor.to_list(length=None)
        except Exception:
            return []

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        try:
            result = await self.database[collection].insert_one(document)
            return str(result.inserted_id)
        except Exception:
            return ""

    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        try:
            result = await self.database[collection].update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception:
            return False

    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        try:
            result = await self.database[collection].delete_one(query)
            return result.deleted_count > 0
        except Exception:
            return False
