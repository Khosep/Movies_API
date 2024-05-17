from functools import lru_cache
from pprint import pprint
from typing import Optional, Annotated
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl.response import Hit
from fastapi import Depends, Request
from redis.asyncio import Redis

from api.v1.schemas.film_schema import FilmDetails
from api.v1.schemas.query_params import SearchParam
from core.config import redis_settings, es_settings
from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import ElasticsearchDBService, RedisCacheService


class PersonService:
    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, index_name):
        # super().__init__(elastic, redis)
        self.es_service = ElasticsearchDBService(elastic)
        self.redis_service = RedisCacheService(redis)
        self.index_name = index_name

    async def get_film_by_uuid(self, film_id: UUID, request: Request) -> FilmDetails | None:

        # retrieve data from redis cache if exists
        # if film := await self.redis_service.retrieve_from_cache(request):
        #     return film
        # retrieve data from elastic
        film = await self.es_service.get_by_id(self.index_name, film_id)

        # add data to redis cache
        # await self.redis_service.add_to_cache(request, film)

        return film


    async def get_person_by_title(self, film_title: str, request: Request) -> list[Hit] | None:

        # retrieve data from redis cache if exists
        # if film := await self.redis_service.retrieve_from_cache(request):
        #     return film
        # retrieve data from elastic
        obj_in = {'title': film_title}
        print(f'f-s_gfbt {obj_in=}')
        films = await self.es_service.get(self.index_name, obj_in)
        # add data to redis cache
        # await self.redis_service.add_to_cache(request, film)

        return films

    # TODO Реализовать поиск по нескольким условиям (возможно объединение с get_film_by_title)
    async def get_person_by_fields(self, film_title: str, request: Request) -> list[Hit] | None:

        # retrieve data from redis cache if exists
        # if film := await self.redis_service.retrieve_from_cache(request):
        #     return film
        # retrieve data from elastic
        obj_in = {'title': film_title}
        print(f'f-s_gfbt {obj_in=}')
        films = await self.es_service.get(self.index_name, obj_in)
        # add data to redis cache
        # await self.redis_service.add_to_cache(request, film)

        return films






    async def get_persons_by_search(self, query_params: SearchParam, request: Request) -> FilmDetails | None:

        #TODO Page processing logic is needed

        # retrieve data from redis cache if exists
        if film := await self.redis_service.retrieve_from_cache(request):
            return film

        #TODO all query_params?
        # retrieve data from elastic
        films = await self.es_service.get_list(self.index_name, query_params)

        # add data to redis cache
        await self.redis_service.add_to_cache(request, films)

        return films if films else None


@lru_cache()
def get_person_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> PersonService:
    print(f'f_ser: {elastic=}')
    return PersonService(elastic, redis, index_name=es_settings.es_indexes['persons']['index_name'])
