from typing import Any, Optional

from aiochclient import ChClient
from utils.abstract import AnalyticDatabaseService
from utils.logger import logger
from utils.sql_queries import MOVIE_DETAILS_QUERY, MOVIE_FILTERS_QUERY, MOVIE_PROGRESS_QUERY


class ClickHouseAdapter(AnalyticDatabaseService):
    LOGNAME = "ClickHouseAdapter"

    def __init__(self, client: ChClient):
        self.client = client

    async def init(self):
        try:
            await self.execute(MOVIE_PROGRESS_QUERY["create_table"])
            await self.execute(MOVIE_FILTERS_QUERY["create_table"])
            await self.execute(MOVIE_DETAILS_QUERY["create_table"])
            logger.info(f"[{self.LOGNAME}] ClickHouse init tables created successfully")
        except Exception as e:
            logger.error(f"[{self.LOGNAME}] Error occurred while creating init tables: {str(e)}")

    async def execute(
            self,
            query: str,
            *args,
            params: Optional[Any] = None,
            query_id: Optional[str] = None
    ) -> Any:
        try:
            if not query.strip().upper().startswith("CREATE"):
                logger.info(f'[{self.LOGNAME}] Executing query with params/args...')
                result = await self.client.execute(
                    query, *args, params=params, query_id=query_id
                )
            else:
                logger.info(f'[{self.LOGNAME}] Executing query without params/args...')
                result = await self.client.execute(query, query_id=query_id)

            logger.info(f"[{self.LOGNAME}] Query executed successfully: {query}")
            return result
        except Exception as e:
            logger.error(f"[{self.LOGNAME}] Error executing {query}: {e}")
            raise

    async def fetch(
        self,
        query: str,
        params: Optional[Any] = None,
        query_id: Optional[str] = None,
        decode: bool = True
    ) -> Any:
        try:
            return await self.client.fetch(
                query,
                params=params,
                query_id=query_id,
                decode=decode
            )
        except Exception as e:
            logger.error(f"[{self.LOGNAME}] Error on fetch: {e}")
            return None

    async def health_check(self) -> Any:
        try:
            response = await self.fetch("SELECT version()")
            if response:
                logger.info(f"[{self.LOGNAME}] Successfully connected")
            else:
                logger.error(f"[{self.LOGNAME}] Failed to get response: {response}")
        except Exception as e:
            logger.error(f"[{self.LOGNAME}] Error occurred while connecting: {str(e)}")
