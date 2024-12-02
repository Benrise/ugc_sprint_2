from datetime import datetime

from .enums import EventType


def get_topic_name(event_type: EventType) -> str:
    return f"{event_type}-events"


def prepare_event_data(data: dict, user_id: str) -> dict:
    data["date_event"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["user_id"] = user_id

    return data
