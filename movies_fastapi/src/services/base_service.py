import logging.config
from abc import ABC, abstractmethod
from uuid import UUID

import orjson
from elasticsearch import NotFoundError, AsyncElasticsearch
from fastapi import Request
from redis.asyncio import Redis

from src.core.config import app_settings, redis_settings
from src.core.exeptions import ElasticsearchError
from src.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class DBService(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        raise NotImplementedError


class ElasticsearchDBService(DBService):
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    async def get(self, index_name: str, doc_id: UUID) -> dict | None:
        """Get item by id (uuid)."""

        try:
            doc = await self.es_client.get(index=index_name, id=str(doc_id))
            item = doc['_source']
            print(f'bs->{type(item)=}')
            return item

        except NotFoundError:
            return None

    async def get_list(self, index_name: str, query: str) -> list[dict] | None:
        """Get list of items by search."""

        try:
            search_result = await self.es_client.search(index=index_name, body=query)
            # TODO DELETE
            # docs = [model_class(**doc["_source"]) for doc in search_result["hits"]["hits"]]
            print(f'"{query}": {search_result=}')
            print(f'\n {search_result["hits"]["hits"]=}')
            docs = [doc["_source"] for doc in search_result["hits"]["hits"]]
            print(f'\n{docs=}')
            return docs
        except ElasticsearchError as e:
            logger.error(f"Ошибка Elasticsearch: {e}")
            return None


class CacheService(ABC):

    @abstractmethod
    async def add_to_cache(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def retrieve_from_cache(self, *args, **kwargs):
        raise NotImplementedError


class RedisCacheService(CacheService):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def add_to_cache(self, request: Request, data: dict | list[dict]) -> None:
        """Put data to cache."""

        key = str(request.url)
        value = orjson.dumps(data)
        await self.redis_client.set(
            name=key,
            value=value,
            ex=redis_settings.redis_cache_expiration_time_sec
        )

    async def retrieve_from_cache(self, request: Request) -> list[dict] | None:
        """Get data from cache."""

        key = str(request.url)
        json_data = await self.redis_client.get(key)
        return orjson.loads(json_data) if json_data else None
