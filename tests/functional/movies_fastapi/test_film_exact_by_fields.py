import json
from copy import deepcopy
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.film_data import get_films_to_load, film_to_load

INDEX_NAME = IndexName.MOVIES.value
ENDPOINT_EXACT_SEARCH = f'{test_settings.prefix}/{INDEX_NAME}/exact_search'


@pytest.mark.parametrize(
    'request_data, expected_response',
    [
        (
                {
                    'uuid': '11111111-1111-1111-1111-111111111111',
                    'title': 'film 1',
                    'imdb_rating': 10
                },
                {'length': 1, 'status': HTTPStatus.OK},
        ),
        (
                {
                    'title': 'film 1',
                    'imdb_rating': 10,
                },
                {'length': 2, 'status': HTTPStatus.OK},
        ),
        (
                {'title': 'film 1'},
                {'length': 3, 'status': HTTPStatus.OK},
        ),
        (
                {'imdb_rating': 10},
                {'length': 3, 'status': HTTPStatus.OK},
        ),
        (
                {
                    'title': 'film 1',
                    'imdb_rating': 1,
                },
                {'length': 1, 'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'imdb_rating': 11},
                {'length': 1, 'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_film_by_fields_status(
        es_load, make_post_request, request_data, expected_response):
    """Check the success of the data return"""

    film_data_in = [
        *get_films_to_load(2, title='film 1', rating=10),
        *get_films_to_load(1, title='film 1', rating=8),
        *get_films_to_load(1, title='film 2', rating=10),
        *get_films_to_load(1, title='film 3', rating=7),
    ]
    endpoint = ENDPOINT_EXACT_SEARCH
    target_uuid = '11111111-1111-1111-1111-111111111111'
    film_data_in[0]['uuid'] = target_uuid

    # load data to elastic
    await es_load(INDEX_NAME, film_data_in)

    response = await make_post_request(
        endpoint,
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )

    assert response['status'] == expected_response['status']
    assert len(response["body"]) == expected_response['length']
    if expected_response['status'] == HTTPStatus.NOT_FOUND:
        assert response['body'] == {'detail': 'Films not found'}
    if expected_response['status'] == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert response['body']['detail'][0]['type'] == 'value_error'


async def test_film_by_fields_fields(
        es_load,
        make_post_request,
):
    """Check the correctness and completeness of the data return."""

    film_data_in = [
        *get_films_to_load(2, title='film 1', rating=10),
        *get_films_to_load(1, title='film 1', rating=8),
        *get_films_to_load(1, title='film 2', rating=10),
        *get_films_to_load(1, title='film 3', rating=7),
    ]
    endpoint = ENDPOINT_EXACT_SEARCH
    target_title = 'film 1'
    target_rating = 10
    request_data = {'title': target_title, 'imdb_rating': target_rating}
    target_response = [film for film in film_data_in
                       if film['title'] == target_title and film['imdb_rating'] == target_rating]

    await es_load(INDEX_NAME, film_data_in)
    response = await make_post_request(
        endpoint,
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )

    assert response['body'] == target_response
    assert response['status'] == HTTPStatus.OK


async def test_film_by_fields_cache(
        es_load,
        make_post_request,
        redis_client: Redis,
):
    """Check the cache operation."""

    film_data_in = deepcopy(film_to_load['film 1'])
    endpoint = ENDPOINT_EXACT_SEARCH

    film_title = film_data_in['title']
    new_film_title = 'New film title'

    request_data = {'title': film_title}

    # 1) load data to elastic (Just 'film_title' are enough)
    await es_load(INDEX_NAME, [film_data_in])
    # make post request
    response = await make_post_request(
        endpoint,
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )

    assert response['body'][0]['title'] == film_title

    # 2) Change the name of the film in the elastic document to 'new_film_title (uuid is the same)'
    # film_data_in = {'uuid': film_data_in['uuid'], 'title': new_film_title}
    film_data_in['title'] = new_film_title
    await es_load(INDEX_NAME, [film_data_in])

    # make the same request as in the first stage
    response = await make_post_request(
        endpoint,
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )

    # Check that the cache is working - the old name ('film_title') has returned from the cache
    assert response['body'][0]['title'] == film_title

    # 3) Reset the redis cache. Now the search for the previous name does not find anything.
    await redis_client.flushall()
    response = await make_post_request(
        endpoint,
        data=json.dumps(request_data),
        headers={"Content-Type": "application/json"},
    )

    assert response['status'] == HTTPStatus.NOT_FOUND
