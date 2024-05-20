import logging.config
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic
from uuid import UUID

import orjson
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q, AsyncSearch, Index
from pydantic import BaseModel
from redis.asyncio import Redis

from core.config import redis_settings, es_settings
from core.logger import LOGGING
from core.utils import cache

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class DBService(ABC):

    @abstractmethod
    async def get_by_id(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_exact_match(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        raise NotImplementedError


GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
QueryParamsSchemaType = TypeVar("QueryParamsSchemaType", bound=BaseModel)


class ElasticsearchDBService(DBService, Generic[GetSchemaType]):
    def __init__(self, es_client: AsyncElasticsearch, redis: Redis):
        self.es_client = es_client
        self.cache_service = RedisCacheService(redis)

    @cache
    async def get_by_id(self, index_name: str, doc_id: UUID) -> dict[str, Any] | None:

        try:
            s = AsyncSearch(using=self.es_client, index=index_name)
            s = s.filter('term', uuid=str(doc_id))
            response = await s.execute()
            doc = response.hits.hits[0]['_source'].to_dict()
            return doc
        except IndexError:
            return None
        except Exception as e:
            print(f'Error in get: {e}')
            raise e

    @cache
    async def get_exact_match(self, index_name: str, obj_in: GetSchemaType) -> list[dict[str, Any]] | None:
        """Get item by fields - exact match."""

        proper_obj_in = await self._transform_fields(index_name, obj_in)
        try:
            s = AsyncSearch(using=self.es_client, index=index_name)
            for field, value in proper_obj_in.items():
                s = s.filter('term', **{field: value})
            total_found = await s.count()  # For informational purposes only
            logger.info('{} documents found'.format(total_found))

            docs = [hit.to_dict() async for hit in s]
            logger.info('{} documents to response'.format(len(docs)))
            return docs
        except IndexError:
            return None
        except Exception as e:
            print(f'Error in get: {e}')
            raise e

    async def _transform_fields(self, index_name: str, data: GetSchemaType) -> dict[str, Any]:
        """Transform fields that can have an exact search in their raw form"""
        # For the 'title' field: it is additionally possible to search for an exact match
        # (but field name must be different: 'title.raw')

        proper_data = data.model_dump(exclude_none=True)
        field_names = list(proper_data.keys())

        # get mapping from index
        indx = Index(index_name, using=self.es_client)
        mapping = await indx.get_mapping()
        field_mapping = mapping[index_name]['mappings']['properties']
        raw_pattern = {'raw': {'type': 'keyword'}}

        # change name of field (adding ".raw" if field has "keyword") for search purposes
        for field in field_names:
            fm_field = field_mapping[field]
            match fm_field:
                case {'type': 'text', 'fields': raw_pattern}:
                    proper_data[f'{field}.raw'] = proper_data.pop(field)
        return proper_data

    @cache
    async def get_list(self, index_name: str, query_params: QueryParamsSchemaType) -> list[dict]:
        """Get list of items by search."""

        s = AsyncSearch(using=self.es_client, index=index_name)

        if query_params.query:
            serch_params = {es_settings.es_indexes[index_name]['search_fields'][0]: query_params.query}
            query = Q("match", **serch_params)
            s = s.query(query)

        # s = s.sort('_score') # sort by relevance (by default, it seems like it should be)
        if 'sort' in query_params.model_fields and query_params.sort is not None:
            s = s.sort(query_params.sort)

        if 'genre_name' in query_params.model_fields and query_params.genre_name is not None:
            # filter_query = Q('terms', genres=query_params.genre)
            filter_query = Q('nested', path='genres', query=Q('match', genres__name=query_params.genre_name))

            s = s.filter(filter_query)  # equivalent: "s = s.query(filter_query)"

        from_item = (query_params.page_number - 1) * query_params.page_size
        s = s[from_item:query_params.page_number * query_params.page_size]
        # s = s[from_=from_item, size=query_params.page_size]

        total_found = await s.count()  # For informational purposes only
        logger.info('{} documents found'.format(total_found))

        docs = [hit.to_dict() async for hit in s]
        logger.info('{} documents to response'.format(len(docs)))

        return docs


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
        self.expiration_time_sec = redis_settings.redis_cache_expiration_time_sec

    async def add_to_cache(self, key: str, data: dict | list[dict]) -> None:
        """Put data to cache."""

        value = orjson.dumps(data)
        await self.redis_client.set(
            name=key,
            value=value,
            ex=self.expiration_time_sec
        )

    async def retrieve_from_cache(self, key: str) -> list[dict] | None:
        """Get data from cache."""

        json_data = await self.redis_client.get(key)
        return orjson.loads(json_data) if json_data else None
