from copy import deepcopy
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.person_data import person_to_load, get_persons_to_load

INDEX_NAME = IndexName.PERSONS.value
ENDPOINT_PERSON_SEARCH = f'{test_settings.prefix}/{INDEX_NAME}/search'


@pytest.mark.parametrize(
    'query_params, expected_response',
    [
        (
                {'query': 'John Logan'},
                {'length': 3, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'Logan'},
                {'length': 2, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'John'},
                {'length': 2, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'HELEN'},
                {'length': 1, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'Not found'},
                {'length': 1, 'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'query': ''},
                {'length': 1, 'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_person_search_status(
        es_load, make_get_request, query_params, expected_response
):
    """Check the success of the data return"""

    person_data_in = person_to_load
    endpoint = ENDPOINT_PERSON_SEARCH

    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint, query_params)

    assert response['status'] == expected_response['status']


async def test_person_search_fields(
        es_load,
        make_get_request,
):
    """Check the correctness and completeness of the data return."""

    person_data_in = person_to_load
    endpoint = ENDPOINT_PERSON_SEARCH
    query_params = {'query': 'Helen'}

    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint, query_params)

    assert response['body'] == [person_to_load[1]]
    assert response['status'] == HTTPStatus.OK


@pytest.mark.parametrize(
    'params, expected_order',
    [
        (
                {'query': 'John Logan'},
                {
                    'status': HTTPStatus.OK,
                    'order': [
                        'John Logan',
                        'Helen Logan',
                        'John Knoll',
                    ],
                },
        ),
        (
                {'query': 'Logan Helen'},
                {
                    'status': HTTPStatus.OK,
                    'order': [
                        'Helen Logan',
                        'John Logan',
                    ],
                },
        ),
        (
                {'query': 'John KnollS'},
                {
                    'status': HTTPStatus.OK,
                    'order': [
                        'John Knoll',
                        'John Logan',
                    ],
                },
        ),
    ],
)
async def test_person_search_relevance(
        es_load, make_get_request, params, expected_order
):
    """Check the correct return order."""

    person_data_in = person_to_load
    endpoint = ENDPOINT_PERSON_SEARCH

    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint, params)
    received_order = [person['full_name'] for person in response['body']]

    assert response['status'] == expected_order['status']
    assert received_order == expected_order['order']


@pytest.mark.parametrize(
    'page_params, expected_response',
    [
        (
                {'page_number': 1, 'page_size': 1000},
                {'length': 75, 'status': HTTPStatus.OK},
        ),
        (
                {'page_number': 1, 'page_size': 50},
                {'length': 50, 'status': HTTPStatus.OK},
        ),
        (
                {'page_number': 2, 'page_size': 50},
                {'length': 75 - 50, 'status': HTTPStatus.OK},
        ),
        (
                {'page_number': 3, 'page_size': 50},
                {'length': 1, 'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'page_number': 1, 'page_size': -1},
                {'length': 1, 'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
                {'page_number': -1, 'page_size': 50},
                {'length': 1, 'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_film_search_pagination(
        es_load, make_get_request, page_params, expected_response
):
    """Check the pagination parameters."""

    person_data_in = get_persons_to_load(75, full_name='John')
    endpoint = ENDPOINT_PERSON_SEARCH
    params = page_params | {'query': 'John'}

    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint, params)

    assert response['status'] == expected_response['status']
    assert len(response["body"]) == expected_response['length']


async def test_person_search_cache(
        es_load,
        make_get_request,
        redis_client: Redis,
):
    """Check the cache operation."""

    number = 75
    full_name = 'John'
    person_data_in = get_persons_to_load(number, full_name=full_name)
    endpoint = ENDPOINT_PERSON_SEARCH
    page_number = 2
    page_size = 50
    params = {'query': full_name, 'page_number': page_number, 'page_size': page_size}
    length_persons = number - page_size

    # 1) Загружаем данные в эластик
    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint, params)

    assert len(response['body']) == length_persons

    # 2) Подгружаем еще таких же персон и отправляем запрос с теми же параметрами
    add_number = 10
    person_data_in = get_persons_to_load(add_number, full_name=full_name)
    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint, params)
    # Проверяем, что кэш работает - вернулось старое количество ответов (персон) из кэша
    assert len(response['body']) == length_persons

    # 3) Сбрасываем кэш. Теперь возвращается количество с учетом добавленных персон
    await redis_client.flushall()
    response = await make_get_request(endpoint, params)

    assert len(response['body']) == length_persons + add_number
