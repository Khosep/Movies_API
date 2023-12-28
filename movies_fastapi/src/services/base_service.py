from abc import ABC, abstractmethod
from uuid import UUID

from elasticsearch import NotFoundError, AsyncElasticsearch
from redis.asyncio import Redis


class Repository(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        raise NotImplementedError


class ElasticsearchRepository(Repository):
    def __init__(self, es_client: AsyncElasticsearch, redis_client: Redis, index_name: str):
        self.es_client = es_client
        self.redis_client = redis_client
        self.index_name = index_name

    async def get(self, doc_id: UUID, index_name: str) -> dict | None:
        try:
            doc = await self.es_client.get(index=index_name, id=doc_id)
        except NotFoundError:
            return None
        return doc

    async def get_list(self, *args, **kwargs):
        raise NotImplementedError



