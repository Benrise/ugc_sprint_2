from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from schemas.bookmark import Bookmark
from schemas.film import FilmRating
from schemas.review import Review, ReviewLike
from utils.abstract import AsyncNoSQLDatabaseService

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
            result: List[Dict[str, Any]] = await cursor.to_list(length=None)
            return result
        except Exception:
            result = []
            return result

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        try:
            response = await self.database[collection].insert_one(document)
            return str(response.inserted_id)
        except Exception:
            return "Error on insert"

    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        try:
            response = await self.database[collection].update_one(query, {"$set": update})
            result: bool = response.modified_count > 0
            return result
        except Exception:
            return False

    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        try:
            response = await self.database[collection].delete_one(query)
            result: bool = response.deleted_count > 0
            return result
        except Exception:
            return False
