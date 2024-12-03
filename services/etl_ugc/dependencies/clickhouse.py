from aiochclient import ChClient
from aiohttp import ClientSession
from db.clickhouse import ClickHouseAdapter
from utils.abstract import AnalyticDatabaseService


async def get_clickhouse_service(session: ClientSession, url: str) -> AnalyticDatabaseService:
    client = ChClient(session, url=url)
    return ClickHouseAdapter(client)
