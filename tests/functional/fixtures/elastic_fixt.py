from typing import AsyncGenerator

import pytest
from elasticsearch import AsyncElasticsearch, helpers

from functional.settings import IndexName, index_settings, test_settings


@pytest.fixture(scope='session')
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    """Create the client to work with Elasticsearch. At the end, we close it."""

    client = AsyncElasticsearch(hosts=[test_settings.es_url])
    yield client
    await client.close()


@pytest.fixture(autouse=True)
async def create_indexes(es_client: AsyncElasticsearch):
    """Create indexes for Elasticsearch, having previously deleted the old ones."""

    for index_name in IndexName:
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(
            index=index_name,
            mappings=index_settings.mappings[index_name],
            settings=index_settings.settings,
        )


@pytest.fixture
def es_load(es_client: AsyncElasticsearch):
    """Entering the data into Elastic."""

    async def inner(index_name: str, data: list[dict]):
        actions = [
            {
                '_index': index_name,
                '_id': row['uuid'],
                '_source': row,
            }
            for row in data
        ]
        await helpers.async_bulk(es_client, actions, refresh=True)
        # refresh=True: The default refresh interval in Elasticsearch is 1 second,
        # which means that changes are automatically made visible for search queries every second.
        # However, setting refresh=True in the bulk insert operation bypasses this interval
        # and forces a refresh immediately after the bulk insert completes.

    return inner
