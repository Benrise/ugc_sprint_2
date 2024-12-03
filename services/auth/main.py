from datetime import datetime
import logging
from contextlib import asynccontextmanager

import uvicorn
from api.v1 import roles, users
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from core.config import settings
from core.logger import LOGGING
from utils.logger import logger
from db import redis
from dependencies.jwt import get_current_user_global
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware

from hawkcatcher import Hawk

hawk = Hawk(settings.hawk_integration_token)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await FastAPILimiter.init(redis.redis)
    if settings.enable_tracing:
        configure_tracer()
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    default_response_class=ORJSONResponse,
    docs_url="/auth/api/v1/docs",
    openapi_url="/auth/api/v1/docs.json",
    lifespan=lifespan,
    dependencies=[Depends(RateLimiter(times=5, seconds=10))],
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key_session)


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider(
        resource=Resource.create({SERVICE_NAME: "auth-service"})
    ))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.tracer_host,
                agent_port=settings.tracer_port,
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


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


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(users.router, prefix='/auth/api/v1/users',
                   tags=['users'], dependencies=[Depends(get_current_user_global)])
app.include_router(roles.router, prefix='/auth/api/v1/roles',
                   tags=['roles'], dependencies=[Depends(get_current_user_global)])

FastAPIInstrumentor.instrument_app(app)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=settings.service_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
