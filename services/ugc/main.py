import logging
import uvicorn
import datetime

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from api.v1 import producer

from core.config import settings
from core.logger import LOGGING

from dependencies import kafka


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka.kafka_producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id='ugc'
        )
    kafka.kafka_consumer = AIOKafkaConsumer(
            group_id=settings.kafka_group_id,
            bootstrap_servers=settings.kafka_bootstrap_servers
        )

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


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
    }

app.include_router(producer.router, prefix='/ugc/api/v1/produce', tags=['produce'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=settings.service_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
