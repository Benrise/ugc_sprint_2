from services.event import UGCEventService
from core.config import settings

ugc_base_url: str | None = f'http://{settings.ugc_host}:{settings.ugc_port}/ugc/api/v1/produce'


def get_ugc_service() -> UGCEventService:
    return UGCEventService(ugc_base_url)
