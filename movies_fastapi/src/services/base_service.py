import logging.config
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic
from uuid import UUID

import orjson
from elasticsearch import NotFoundError, AsyncElasticsearch
from elasticsearch_dsl import Search, Q, AsyncSearch, async_connections, Index
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl.response import Hit
from fastapi import Request
from pydantic import BaseModel
from redis.asyncio import Redis

from api.v1.schemas.film_schema import FilmQueryExact
from api.v1.schemas.query_params import SearchParam
from core.config import app_settings, redis_settings, es_settings
from core.exeptions import ElasticsearchError
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class DBService(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        raise NotImplementedError

GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)

class ElasticsearchDBService(DBService, Generic[GetSchemaType]):
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    # TODO Delete Sample from official documentation
    # from elasticsearch_dsl import AsyncSearch


    # async_connections.create_connection('conn1', hosts=es_settings.es_url, timeout=20)
    # doc = await self.es_client.get(index=index_name, id=str(doc_id))
    # item = doc['_source']
    # print(f'bs->{type(item)=}')
    # return item
    # async def run_query():
    #     q = Match(title={"query": "web framework", "type": "phrase"})
    #     s = AsyncSearch(index="my-index") \
    #         .filter("term", category="search") \
    #         .query("match", title="python") \
    #         .exclude("match", description="beta")
    #     async for hit in s:
    #         print(hit.title)

    # async def run_query():
    #     s = AsyncSearch(index="my-index")
    #     .filter("term", category="search")
    #     .query("multi_match", query="python", fields=["title", "description"])
    #     .exclude("match", description="beta")
    #
    #     async for hit in s:
    #         print(hit.title)

    # async def get_by_uuid(self, index_name: str, doc_id: UUID):
    #     doc = await self.es_client.get(index=index_name, id=str(doc_id))
    #     item = doc['_source']
    #     print(f'bs->{type(item)=}')
    #     return item


    async def get_by_id(self, index_name: str, doc_id: UUID):

        try:
            s = AsyncSearch(using=self.es_client, index=index_name)
            s = s.filter('term', uuid=str(doc_id))
            response = await s.execute()
            result = response.hits.hits[0]['_source']
            print(f'get_by_uuid: {type(result)=}')
            return result
        except IndexError:
            return None
        except Exception as e:
            print(f'Error in get: {e}')
            raise e


    async def get(self, index_name: str, obj_in: GetSchemaType) -> list[Hit] | None:
        """Get item by fields - exact match."""

        proper_obj_in = await self._transform_fields(index_name, obj_in)
        print(f' bs:{proper_obj_in=}')
        try:
            s = AsyncSearch(using=self.es_client, index=index_name)
            # Option: To make this method universal, which is accessed from different endpoits (and as a result, service funcs)
            for field, value in proper_obj_in.items():
                s = s.filter('term', **{field: value})

            # TODO Delete
            total = await s.count()
            print(f' bs:{total=}')

            results = [hit async for hit in s]

            #TODO Delete
            print(f'base_serv: {len(results)=}')
            print(f'base_serv: {results=}')
            results_titles = [hit.title async for hit in s]
            print(f'base_serv: {results_titles=}')
            async for hit in s:
                print(f'base_serv: {hit.title=}')

            return results
        except IndexError:
            return None
        except Exception as e:
            print(f'Error in get: {e}')
            raise e

    # async def get(self, index_name: str, doc_id: UUID) -> dict | None:
    #     """Get item by id (uuid)."""
    #
    #     try:
    #         doc = await self.es_client.get(index=index_name, id=str(doc_id))
    #         item = doc['_source']
    #         print(f'bs->{type(item)=}')
    #         return item
    #
    #     except NotFoundError:
    #         return None

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








        # field_mapping = [mapping[index_name]['mappings']['properties'][field] for field in field_names]

        # print(f' bs:{field_mapping=}')
        # # print(f' bs:{mapping0[index_name]["mappings"]["properties"]=}')
        # f_mapping = await indx.get_field_mapping(fields=[field_names])
        # print(f' bs:{f_mapping=}')
        # # f1_mapping0 = await indx.get_field_mapping(fields=['title'])
        # # print(f' bs:{f1_mapping0=}')
        #
        # mapping1 = await self.es_client.indices.get_mapping(index=index_name)
        # print(f' bs:{mapping1=}')
        # # TODO hardcode (requires a loop (obj_in.keys())
        # # field_names = ['uuid', 'title', 'imdb_rating', 'genres', 'actors']
        # for field in field_names:
        #     # field_name = 'title'
        #     field_mapping = mapping1[index_name]['mappings']['properties'][field]
        #     print(f'---bs:{field} --> {field_mapping=}')
        #
        # f_mapping2 = await self.es_client.indices.get_field_mapping(index=index_name, fields=[field_names])
        # print(f' bs:{f_mapping2=}')
        # f1_mapping3 = await self.es_client.indices.get_field_mapping(index=index_name, fields=['title'])
        # print(f' bs:{f1_mapping3=}')



    async def get_list(self, index_name: str, query_params: SearchParam) -> list[dict] | None:
        """Get list of items by search."""

        if query_params.query:
            search_query = self._get_search_query(index_name, query_params)

            body = self._get_es_query(query_params)

            try:
                search_result = await self.es_client.search(
                    index=index_name,
                    body=body,
                )
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

    async def _get_search_query(self,
                                index_name: str,
                                query_params: SearchParam
                                ):
        s = Search(using=self.es_client).index(index_name)
        # Define search fields
        s = s.query('multi_match',
                    query=query_params.query,
                    fields=es_settings.es_indexes['movies']['search_fields'])
        #TODO add pagination (sort and filter (genre) are not needed here) and fuzzy

    async def _get_filter_and_sort_query(self,
                                index_name: str,
                                query_params: SearchParam
                                ):
        #TODO Но здесь не через Search (искать нечего - нужен только лист), а как?
        s = Search(using=self.es_client)

        # Фильтр по жанрам
        filter_query = Q('terms', genres=query_params.genre)
        s = s.query(filter_query)

        # # Полнотекстовый поиск по названию книги
        # s = s.query("multi_match", query=search_text, fields=["title"])
        #
        # # Выполняем поиск
        # response = s.execute()
        #
        # # Обрабатываем результаты
        # for hit in response:
        #     # Обработка найденных документов
        #     print(hit.title)






    #TODO Remove
    async def _get_es_query(self,
                            query_params,
                            matches: dict = None,
                            bool_operator: str = 'should'
                            ):
        pass
        # if query_params.sort:
        #
        #     sort = query_params.sort if query_params else ''
        #
        #
        #
        #
        # body = {
        #     'query': {
        #         'match': {
        #             'title': query_params.query
        #         }
        #     }
        # }
        #
        # body = {
        #     "query": {
        #         "bool": {
        #             "must": {
        #                 "match": {
        #                     "title": query_params.query
        #                 }
        #             }
        #         }
        #     }
        # }
        #
        # if query_params.page_size:
        #     body['size'] = query_params.page_size
        #     body['from_'] = query_params.page_size * (query_params.page_number - 1)
        #
        # if query_params.sort:
        #     body['sort'] = [
        #         {
        #             "imdb_rating": {
        #                 "order": query_params.sort
        #             }
        #         }
        #     ]




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
