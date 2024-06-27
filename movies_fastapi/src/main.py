from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import base_api, film_api, person_api, genre_api
from core.config import app_settings, redis_settings, es_settings
from db import elastic
from db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis.redis = Redis.from_url(redis_settings.redis_url)
    elastic.es = AsyncElasticsearch(es_settings.es_url)
    yield
    # Finish (clean up and release the resources)
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
    # TODO Delete
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(base_api.router, tags=[app_settings.tag_service])
app.include_router(film_api.router, prefix=app_settings.prefix + '/films', tags=[app_settings.tag_films])
app.include_router(person_api.router, prefix=app_settings.prefix + '/persons', tags=[app_settings.tag_persons])
app.include_router(genre_api.router, prefix=app_settings.prefix + '/genres', tags=[app_settings.tag_genres])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
        reload=True,
    )
