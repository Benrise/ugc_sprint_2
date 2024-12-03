from beanie import init_beanie
from core.config import settings
from db.mongodb import MongoDocuments
from dependencies import mongodb
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from utils.logger import logger


async def init_mongodb():
    LOGNAME = "MongoDB"

    try:
        mongodb.mongodb = AsyncIOMotorClient(settings.mongodb_base_url)
        logger.info(f"[{LOGNAME}] Проверка соединения с MongoDB...")
        await mongodb.mongodb.admin.command("ping")
        logger.info(f"[{LOGNAME}] MongoDB доступен.")

        logger.info(f"[{LOGNAME}] Инициализация Beanie...")
        await init_beanie(
            database=mongodb.mongodb[settings.mongodb_database_name],
            document_models=MongoDocuments
        )
        logger.info(f"[{LOGNAME}] Beanie успешно инициализирован.")

    except ConnectionFailure as e:
        logger.error(f"[{LOGNAME}] Не удалось подключиться к MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"[{LOGNAME}] Ошибка при инициализации MongoDB: {e}")
        raise
