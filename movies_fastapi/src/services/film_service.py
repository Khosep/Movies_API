from functools import lru_cache
from pprint import pprint
from typing import Optional, Annotated
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, Request
from redis.asyncio import Redis

from src.api.v1.schemas.film_schema import FilmDetails
from src.api.v1.schemas.query_params import SearchParam
from src.core.config import redis_settings, es_settings
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film_model import Film
from src.services.base_service import ElasticsearchDBService, RedisCacheService


class FilmService:
    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, index_name):
        # super().__init__(elastic, redis)
        self.es_service = ElasticsearchDBService(elastic)
        self.redis_service = RedisCacheService(redis)
        self.index_name = index_name

    async def get_film_by_uuid(self, film_id: UUID, request: Request) -> FilmDetails | None:

        # retrieve data from redis cache if exists
        if film := await self.redis_service.retrieve_from_cache(request):
            return film
        # retrieve data from elastic
        film = await self.es_service.get(self.index_name, film_id)
        # add data to redis cache
        await self.redis_service.add_to_cache(request, film)

        return film if film else None

    async def get_films_by_search(self, query_params: SearchParam, request: Request) -> FilmDetails | None:

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



    # # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    # async def get_by_id(self, film_id: str) -> Optional[Film]:
    #     # Пытаемся получить данные из кеша, потому что оно работает быстрее
    #     film = await self._film_from_cache(film_id)
    #     if not film:
    #         # Если фильма нет в кеше, то ищем его в Elasticsearch
    #         film = await self._get_film_from_elastic(film_id)
    #         if not film:
    #             # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
    #             return None
    #         # Сохраняем фильм  в кеш
    #         await self._put_film_to_cache(film)
    #
    #     return film
    #
    # async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
    #     try:
    #         doc = await self.elastic.get(index='movies', id=film_id)
    #     except NotFoundError:
    #         return None
    #     return Film(**doc['_source'])
    #
    # async def _film_from_cache(self, film_id: str) -> Optional[Film]:
    #     # Пытаемся получить данные о фильме из кеша, используя команду get
    #     # https://redis.io/commands/get/
    #     data = await self.redis.get(film_id)
    #     if not data:
    #         return None
    #
    #     # pydantic предоставляет удобное API для создания объекта моделей из json
    #     # film = Film.parse_raw(data)
    #     film = Film.model_validate_json(data)
    #     return film
    #
    # async def _put_film_to_cache(self, film: Film):
    #     # Сохраняем данные о фильме, используя команду set
    #     # Выставляем время жизни кеша — 5 минут
    #     # https://redis.io/commands/set/
    #     # pydantic позволяет сериализовать модель в json
    #     await self.redis.set(film.id, film.model_dump_json(), redis_settings.cache_expiration_time_sec)


@lru_cache()
def get_film_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> FilmService:
    print(f'f_ser: {elastic=}')
    return FilmService(elastic, redis, index_name=es_settings.es_indexes['movies']['index_name'])
