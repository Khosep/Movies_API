from functools import lru_cache
from typing import Annotated
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from api.v1.schemas.film_schema import FilmDetails, FilmQueryExact
from api.v1.schemas.query_params import FilmTotalParam, FilmListParam
from core.config import es_settings
from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import ElasticsearchDBService


class FilmService:
    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, index_name: str):
        # super().__init__(elastic, redis)
        self.es_service = ElasticsearchDBService(elastic, redis)
        self.index_name = index_name

    async def get_film_by_uuid(self, film_id: UUID) -> FilmDetails | None:
        film = await self.es_service.get_by_id(self.index_name, film_id)
        return film

    async def get_film_by_fields(self, film_data: FilmQueryExact) -> list[FilmDetails] | None:
        films = await self.es_service.get_exact_match(self.index_name, film_data)
        return films

    async def get_films_by_search(self, query_params: FilmTotalParam) -> list[FilmDetails] | None:
        films = await self.es_service.get_list(self.index_name, query_params)
        return films if films else None  # because an empty sheet may return (in 'films')

    async def get_films_list(self, query_params: FilmListParam) -> list[FilmDetails] | None:
        films = await self.es_service.get_list(self.index_name, query_params)
        return films if films else None  # because an empty sheet may return (in 'films')


@lru_cache()
def get_film_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> FilmService:
    return FilmService(elastic, redis, index_name=es_settings.es_indexes['movies']['index_name'])
