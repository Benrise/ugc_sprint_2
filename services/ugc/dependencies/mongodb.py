from core.config import settings
from db.mongodb import MongoDBAdapter
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from utils.abstract import AsyncNoSQLDatabaseService

mongodb: AsyncIOMotorClient | None = None


async def get_mongo_client() -> AsyncIOMotorClient:
    return mongodb


async def get_mongodb_service(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> AsyncNoSQLDatabaseService:
    return MongoDBAdapter(client, settings.mongodb_database_name)
