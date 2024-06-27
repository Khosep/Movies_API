from logging import Logger
from typing import Generator, Any

import backoff
from elasticsearch import Elasticsearch, helpers


from etl_settings import etl_settings, es_settings, Index
from etl_utils import get_json_data, coroutine
from logger import logger
from state.state import State


class ElasticsearhClient:
    def __init__(self, es_url: str = es_settings.es_url):
        self.es = Elasticsearch(es_url)

    def create_index_if_not_exists(self, index_name, index_path) -> None:
        if not self.es.indices.exists(index=index_name):
            index_schema = get_json_data(index_path)
            self.es.indices.create(
                index=index_name,
                mappings=index_schema['mappings'],
                settings=index_schema['settings']
            )
            logger.info(f'Index "{index_name}" created successfully')


class ElasticsearchLoader:
    def __init__(self, logger: Logger):
        self._logger = logger
        self.client = ElasticsearhClient()


    @coroutine
    @backoff.on_exception(backoff.expo, Exception)
    def load(self, state: State) -> Generator[None, dict[str, Any], None]:
        """Load docs to Elasticsearch."""
        while total_data_in := (yield):
            index_name = total_data_in['index_name']
            data = total_data_in['data']
            last_updated = total_data_in['last_updated']
            self._logger.info(f'Got {len(data)} data for "{index_name}" with latest timestamp={last_updated}')
            self._logger.info(f'First item from data: {data[0]}')

            actions = [{
                '_index': index_name,
                '_id': row['uuid'],
                '_source': row
            } for row in data]

            helpers.bulk(self.client.es, actions)
            self._logger.info(f'Loaded {len(data)} docs')

            state.set_state(f'{index_name}_last_updated', str(last_updated))
            self._logger.info(f'Set in state: last_updated={last_updated}')
