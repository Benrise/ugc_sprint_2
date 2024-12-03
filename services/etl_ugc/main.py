import asyncio

from aiohttp import ClientSession
from core.config import settings
from db.clickhouse import ClickHouseAdapter
from dependencies.clickhouse import get_clickhouse_service
from services.etl import ETLService
from utils.logger import logger


async def main():
    session: ClientSession = ClientSession()
    clickhouse_service: ClickHouseAdapter = (
        await get_clickhouse_service(session, url=settings.clickhouse_url)
    )
    etl_service = ETLService(
        clickhouse_service=clickhouse_service,
        kafka_servers=settings.kafka_bootstrap_servers,
        kafka_topics=settings.kafka_topics,
        batch_size=settings.etl_batch_size
    )

    await clickhouse_service.health_check()

    try:
        logger.info("Starting ETL process")
        await clickhouse_service.init()
        await etl_service.start()
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
