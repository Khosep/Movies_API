from functools import lru_cache
from typing import Annotated
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Request
from redis.asyncio import Redis

from api.v1.schemas.film_schema import FilmDetails
from api.v1.schemas.person_schema import PersonDetails, PersonName
from api.v1.schemas.query_params import SearchParam
from core.config import es_settings
from core.utils import cache
from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import ElasticsearchDBService, RedisCacheService


class PersonService:
    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, index_name: str):
        self.es_service = ElasticsearchDBService(elastic, redis)
        self.redis_service = RedisCacheService(redis)
        self.index_name = index_name

    async def get_person_by_uuid(self, person_id: UUID) -> PersonDetails | None:
        person = await self.es_service.get_by_id(self.index_name, person_id)
        return person

    async def get_person_by_name(self, full_name: str) -> list[PersonDetails] | None:
        obj_in = PersonName(full_name=full_name)
        # Why persons, not a person: because a complete namesake situation is theoretically possible.
        persons = await self.es_service.get_exact_match(self.index_name, obj_in)
        return persons

    async def get_persons_by_search(self, query_params: SearchParam) -> list[PersonDetails] | None:
        persons = await self.es_service.get_list(self.index_name, query_params)
        return persons if persons else None


@lru_cache()
def get_person_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> PersonService:
    return PersonService(elastic, redis, index_name=es_settings.es_indexes['persons']['index_name'])
