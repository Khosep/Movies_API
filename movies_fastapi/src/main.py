from contextlib import asynccontextmanager
from typing import Generator, Any

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from core.config import app_settings, redis_settings, es_settings

from src.db import redis
from api.v1 import base_api, film_api
from src.db import elastic


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis.redis = Redis.from_url(redis_settings.redis_url)
    print(redis.redis)
    elastic.es = AsyncElasticsearch(es_settings.es_url)
    yield
    # Clean up the ML models and release the resources
    await redis.redis.close()
    await elastic.es.close()

app = FastAPI(
    # The name of the project to be displayed in the documentation
    title=app_settings.app_title,
    # Address where the interactive API documentation will be available
    docs_url=app_settings.docs_url,
    # Address where the raw OpenAPI JSON schema will be available
    openapi_url=app_settings.openapi_url,
    # If the JSON-serializer is not explicitly specified in the response,
    # the faster 'ORJSONResponse' will be used instead of the standard 'JSONResponse'
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

#TODO DELETE

# @app.on_event('startup')
# async def startup():
#     # Подключаемся к базам при старте сервера
#     # Подключиться можем при работающем event-loop
#     # Поэтому логика подключения происходит в асинхронной функции
#     redis.redis = Redis(host=redis_settings.redis_host, port=redis_settings.redis_port)
#     # elastic.es = AsyncElasticsearch(hosts=[f'{es_settings.es_host}:{es_settings.es_port}'])
#     elastic.es = AsyncElasticsearch(es_settings.es_url)
#
#
# @app.on_event('shutdown')
# async def shutdown():
#     # Отключаемся от баз при выключении сервера
#     await redis.redis.close()
#     await elastic.es.close()


app.include_router(base_api.router, tags=[app_settings.tag_service])
app.include_router(film_api.router, prefix=app_settings.prefix + '/films', tags=[app_settings.tag_films])
# app.include_router(health_api.router, prefix=app_settings.prefix)
# app.include_router(file_api.router, prefix=app_settings.prefix + '/files')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
        reload=True,
    )
