from functools import lru_cache
from pprint import pprint
from typing import Optional, Annotated, Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl.response import Hit
from fastapi import Depends, Request
from redis.asyncio import Redis

from api.v1.schemas.film_schema import FilmDetails, FilmQueryExact
from api.v1.schemas.query_params import SearchParam, FilmTotalParam
from core.config import redis_settings, es_settings
from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import ElasticsearchDBService, RedisCacheService


class FilmService:
    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, index_name: str):
        # super().__init__(elastic, redis)
        self.es_service = ElasticsearchDBService(elastic, redis)
        # TODO Delete Redis
        self.redis_service = RedisCacheService(redis)
        self.index_name = index_name

    async def get_film_by_uuid(self, film_id: UUID) -> FilmDetails | None:
        film = await self.es_service.get_by_id(self.index_name, film_id)
        return film


    async def get_film_by_fields(self, film_data: FilmQueryExact) -> list[FilmDetails] | None:
        films = await self.es_service.get_exact_match(self.index_name, film_data)
        return films

    # TODO Redo it
    async def get_films_by_search(self, query_params: FilmTotalParam) -> list[FilmDetails] | None:
        # https://www.tipoit.kz/elk-bool-query
        # https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html
        #TODO Page processing logic is needed

        #TODO all query_params?
        films = await self.es_service.get_list(self.index_name, query_params)

        return films if films else None

@lru_cache()
def get_film_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> FilmService:
    return FilmService(elastic, redis, index_name=es_settings.es_indexes['movies']['index_name'])
