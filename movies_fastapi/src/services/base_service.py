import logging.config
from abc import ABC, abstractmethod
from uuid import UUID

import orjson
from elasticsearch import NotFoundError, AsyncElasticsearch
from elasticsearch_dsl import Search, Q
from fastapi import Request
from redis.asyncio import Redis

from src.api.v1.schemas.query_params import SearchParam
from src.core.config import app_settings, redis_settings, es_settings
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
