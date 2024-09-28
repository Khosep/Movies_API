from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.genre_data import genre_to_load

INDEX_NAME = IndexName.GENRES.value
ENDPOINT_LIST_GENRES = f'{test_settings.prefix}/{INDEX_NAME}'


async def test_genre_list_fields(
        es_load,
        make_get_request,
):
    """Check the correctness and completeness of the data return for list of genres."""

    genre_data_in = genre_to_load[:10]
    endpoint = ENDPOINT_LIST_GENRES

    await es_load(INDEX_NAME, genre_data_in)
    response = await make_get_request(endpoint)

    assert response['status'] == HTTPStatus.OK
    assert len(response['body']) == len(genre_data_in)
    assert all(
        [
            set(fields) == {'uuid', 'name'}
            for fields in response['body']
        ]
    )
    assert response['body'][2] in genre_data_in


@pytest.mark.parametrize(
    'page_params, expected_response',
    [
        (
                {'page_number': 1, 'page_size': 1000},
                {'length': 26, 'status': HTTPStatus.OK},
        ),
        (
                {'page_number': 1, 'page_size': 20},
                {'length': 20, 'status': HTTPStatus.OK},
        ),
        (
                {'page_number': 2, 'page_size': 15},
                {'length': 26 - 15, 'status': HTTPStatus.OK},
        ),
        (
                {'page_number': 3, 'page_size': 15},
                {'length': 1, 'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'page_number': 1, 'page_size': -1},
                {'length': 1, 'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
                {'page_number': -1, 'page_size': 25},
                {'length': 1, 'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_genre_list_pagination(
        es_load, make_get_request, page_params, expected_response
):
    """Check the pagination parameters."""

    genre_data_in = genre_to_load
    endpoint = ENDPOINT_LIST_GENRES

    await es_load(INDEX_NAME, genre_data_in)
    response = await make_get_request(endpoint, page_params)

    assert response['status'] == expected_response['status']
    assert len(response["body"]) == expected_response['length']


async def test_genre_list_cache(
        es_load,
        make_get_request,
        redis_client: Redis,
):
    """Checking the operation of the cache for the list of genres."""

    number = 20
    genre_data_in = genre_to_load[:20]
    endpoint = ENDPOINT_LIST_GENRES
    page_number = 2
    page_size = 15
    params = {'page_number': page_number, 'page_size': page_size}
    length_genres = number - page_size

    # 1) Загружаем данные в эластик
    await es_load(INDEX_NAME, genre_data_in)
    response = await make_get_request(endpoint, params)

    assert len(response['body']) == length_genres

    # 2) Подгружаем еще жанры и отправляем запрос с теми же параметрами
    add_number = 5
    genre_data_in = genre_to_load[number:number + add_number]

    await es_load(INDEX_NAME, genre_data_in)
    response = await make_get_request(endpoint, params)

    # Проверяем, что кэш работает - вернулось старое количество жанров из кэша
    assert len(response['body']) == length_genres

    # 3) Сбрасываем кэш. Теперь возвращается количество с учетом добавленных жанров
    await redis_client.flushall()
    response = await make_get_request(endpoint, params)

    assert len(response['body']) == length_genres + add_number
