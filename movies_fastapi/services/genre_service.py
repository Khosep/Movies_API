from functools import lru_cache
from typing import Annotated

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from api.v1.schemas.genre_schema import GenreBase
from api.v1.schemas.query_params import PageParam
from core.config import es_settings
from db.elastic import get_elastic
from db.redis import get_redis
from services.base_service import ElasticsearchDBService


class GenreService:
    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, index_name: str):
        self.es_service = ElasticsearchDBService(elastic, redis)
        self.index_name = index_name

    async def get_genres_list(self, query_params: PageParam) -> list[GenreBase] | None:
        genres = await self.es_service.get_list(self.index_name, query_params)
        return genres if genres else None  # because an empty sheet may return (in 'genres')


@lru_cache()
def get_genre_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> GenreService:
    return GenreService(elastic, redis, index_name=es_settings.es_indexes['genres']['index_name'])
