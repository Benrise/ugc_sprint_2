from datetime import datetime
import logging
from contextlib import asynccontextmanager

import uvicorn
from api.v1 import films, genres, persons
from core.config import settings
from core.logger import LOGGING
from utils.logger import logger
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

from hawkcatcher import Hawk

hawk = Hawk(settings.hawk_integration_token)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f'{settings.elastic_protocol}://{settings.elastic_host}:{settings.elastic_port}'
        ]
    )
    await FastAPILimiter.init(redis.redis)
    yield
    await redis.redis.close()
    await elastic.es.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/movies/api/v1/docs',
    openapi_url='/movies/api/v1/docs.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    dependencies=[Depends(RateLimiter(times=5, seconds=10))],
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})

    logger.info(
        "middleware",
        extra={
            "request_id": request_id,
            "host": settings.service_host,
            "method": request.method,
            "query_params": str(request.query_params),
            "status_code": response.status_code,
            "elapsed_time": (datetime.now() - start_time).total_seconds(),
        }
    )

    return response


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }

app.include_router(films.router, prefix='/movies/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/movies/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/movies/api/v1/persons', tags=['persons'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=settings.service_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
