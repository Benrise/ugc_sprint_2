import json
from typing import Optional

from brokers.kafka import KafkaAdapter
from dependencies.kafka import get_kafka_service
from dependencies.user import get_user_service
from fastapi import APIRouter, Depends, HTTPException, Request, status
from services.user import UserService
from utils.broker import get_topic_name, prepare_event_data
from utils.enums import EventType

router = APIRouter()


@router.post("/send_to_broker/{event_type}")
async def send_to_broker(
    request: Request,
    event_type: EventType,
    event_data: Optional[dict] = {
        "movie_id": "1eb9cc6b-879f-4160-8971-918ecbe47a87",
        "progress": 100.0,
        "status": "completed",
        "last_watched": "2023-11-20 12:32:23",
    },
    user_service: UserService = Depends(get_user_service),
    kafka_service: KafkaAdapter = Depends(get_kafka_service)
):
    user_id = await user_service.get_user_id_from_jwt(request)

    data = await request.json()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data is required")

    data = prepare_event_data(data, user_id)
    topic = get_topic_name(event_type)

    await kafka_service.produce(topic=topic, key=event_type, value=json.dumps(data))

    return {
        "detail": "Event successfully sent to broker",
        "data": data,
        "user_id": user_id,
        "event_type": event_type,
        "topic": topic
    }
