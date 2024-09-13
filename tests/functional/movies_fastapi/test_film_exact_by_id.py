from copy import deepcopy
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.film_data import film_to_load

INDEX_NAME = IndexName.MOVIES.value
ENDPOINT_EXACT_SEARCH = f'{test_settings.prefix}/{INDEX_NAME}/exact_search'


@pytest.mark.parametrize(
    'film_uuid, expected_response',
    [
        (
                {'uuid': '3d825f60-9fff-4dfe-b294-1a45fa1e115d'},
                {'status': HTTPStatus.OK},
        ),
        (
                {'uuid': '00000000-0000-0000-0000-000000000000'},
                {'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'uuid': '88888888-8888-8888-8888-888888888888'},
                {'status': HTTPStatus.OK},
        ),
    ],
)
async def test_film_details_status(
        es_load, make_get_request, film_uuid, expected_response
):
    """Check the success of the data return"""

    film_data_in = [
        film_to_load['film 1'],
        film_to_load['film 2'],
    ]
    endpoint = f'{ENDPOINT_EXACT_SEARCH}/{film_uuid["uuid"]}'
    # load data to elastic
    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint)

    assert response['status'] == expected_response['status']


async def test_film_details_fields(
        es_load,
        make_get_request,
):
    """Check the correctness and completeness of the data return."""

    film_data_in = film_to_load['film 1']
    endpoint = f'{ENDPOINT_EXACT_SEARCH}/{film_data_in["uuid"]}'

    await es_load(INDEX_NAME, [film_data_in])
    response = await make_get_request(endpoint)

    assert response['body'] == film_data_in
    assert response['status'] == HTTPStatus.OK


async def test_film_details_cache(
        es_load,
        make_get_request,
        redis_client: Redis,
):
    """Check the cache operation."""

    film_data_in = deepcopy(film_to_load['film 1'])
    endpoint = f'{ENDPOINT_EXACT_SEARCH}/{film_data_in["uuid"]}'

    film_title = film_data_in['title']
    new_film_title = 'New film title'

    # 1) load data to elastic (Just 'film_title' is enough)
    await es_load(INDEX_NAME, [film_data_in])
    # make get request
    response = await make_get_request(endpoint)

    assert response['body']['title'] == film_title

    # 2) Change the name of the film in the elastic document to 'new_film_title (uuid is the same)'
    # film_data_in = {'uuid': film_data_in['uuid'], 'title': new_film_title}
    film_data_in['title'] = new_film_title
    await es_load(INDEX_NAME, [film_data_in])

    # make the same request as in the first stage
    response = await make_get_request(endpoint)

    # Check that the cache is working - the old name ('film_title') has returned from the cache
    assert response['body']['title'] == film_title

    # 3) Reset the redis cache. Now the current title of the film is returned ('new_film_title')
    await redis_client.flushall()
    response = await make_get_request(endpoint)

    assert response['body']['title'] == new_film_title
