from typing import Any, Optional

from utils.logger import logger
from utils.abstract import AnalyticDatabaseService
from utils.sql_queries import (MOVIE_PROGRESS_QUERY, MOVIE_FILTERS_QUERY, MOVIE_DETAILS_QUERY)

from aiochclient import ChClient


class ClickHouseAdapter(AnalyticDatabaseService):
    def __init__(self, client: ChClient):
        self.client = client

    async def init(self):
        try:
            await self.execute(MOVIE_PROGRESS_QUERY["create_table"])
            await self.execute(MOVIE_FILTERS_QUERY["create_table"])
            await self.execute(MOVIE_DETAILS_QUERY["create_table"])
            logger.info(f"[{self.__class__.__name__}] ClickHouse init tables created successfully")
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Error occurred while creating init tables: {str(e)}")

    async def execute(
            self,
            query: str,
            *args,
            params: Optional[Any] = None,
            query_id: Optional[str] = None
    ) -> Any:
        try:
            if not query.strip().upper().startswith("CREATE"):
                logger.info('Executing query with params/args...')
                result = await self.client.execute(
                    query, *args, params=params, query_id=query_id
                )
            else:
                logger.info('Executing query without params/args...')
                result = await self.client.execute(query, query_id=query_id)

            logger.info(f"[{self.__class__.__name__}] Query executed successfully: {query}")
            return result
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Error executing {query}: {e}")
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
            logger.error(f"[{self.__class__.__name__}] Error on fetch: {e}")
            return None

    async def health_check(self) -> Any:
        try:
            response = await self.fetch("SELECT version()")
            if response:
                logger.info(f"[{self.__class__.__name__}] Successfully connected to ClickHouse")
            else:
                logger.error(f"[{self.__class__.__name__}] Failed to get response from ClickHouse: {response}")
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Error occurred while connecting to ClickHouse: {str(e)}")
