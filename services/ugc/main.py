import datetime
import logging
from contextlib import asynccontextmanager

import uvicorn
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from api.v1 import bookmarks, film_ratings, producer, review_likes, reviews
from core.config import settings
from core.logger import LOGGING
from db.init_db import init_mongodb
from dependencies import kafka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from hawkcatcher.modules.fastapi import HawkFastapi


@asynccontextmanager
async def lifespan(_: FastAPI):
    kafka.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id='ugc'
    )
    kafka.kafka_consumer = AIOKafkaConsumer(
        group_id=settings.kafka_group_id,
        bootstrap_servers=settings.kafka_bootstrap_servers
    )

    await init_mongodb()

    await kafka.kafka_consumer.start()
    await kafka.kafka_producer.start()
    yield
    await kafka.kafka_producer.stop()
    await kafka.kafka_consumer.stop()

app = FastAPI(
    title=settings.project_name,
    docs_url='/ugc/api/v1/docs',
    openapi_url='/ugc/api/v1/docs.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

hawk = HawkFastapi({
    "app_instance": app,
    "token": settings.hawk_integration_token
})


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
    }

app.include_router(producer.router, prefix='/ugc/api/v1/produce', tags=['produce'])
app.include_router(reviews.router, prefix='/ugc/api/v1/reviews', tags=['reviews'])
app.include_router(review_likes.router, prefix='/ugc/api/v1/review_likes', tags=['review_likes'])
app.include_router(film_ratings.router, prefix='/ugc/api/v1/film_ratings', tags=['film_ratings'])
app.include_router(bookmarks.router, prefix='/ugc/api/v1/bookmarks', tags=['bookmarks'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=settings.service_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
