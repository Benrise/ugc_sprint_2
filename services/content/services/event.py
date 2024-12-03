import httpx
from fastapi import Request
from utils.enums import EventType
from utils.logger import logger


class UGCEventService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_event(self, request: Request, event_type: EventType, data: dict):
        url = f"{self.base_url}/send_to_broker/{event_type}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=request.headers)
            if response.status_code != 200:
                logger.error(f"Failed to send event: {response.status_code}")
            return response
