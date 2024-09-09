from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.film_data import (
    film_to_load,
    FILM,
    get_films_to_load,
)

INDEX_NAME = IndexName.MOVIES.value
ENDPOINT_SEARCH = f'{test_settings.prefix}/{INDEX_NAME}/search'


# TODO This is the copy of another test file. Change step by step.

@pytest.mark.parametrize(
    'query_params, expected_response',
    [
        (
                {'query': 'stars'},
                {'length': 3, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'wars'},
                {'length': 2, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'star wars'},
                {'length': 3, 'status': HTTPStatus.OK},
        ),
        (
                {'query': 'SUPERSTAR'},
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
async def test_film_search_status(
        es_load, make_get_request, query_params, expected_response):
    """Check the success of the data return with a fuzzy search"""

    film_data_in = [
        *get_films_to_load(1, title='Star Wars. Episode I: The Phantom Menace', rating=4),
        *get_films_to_load(1, title='Talking to a superstar', rating=10),
        *get_films_to_load(1, title='Starving', rating=8),
        *get_films_to_load(1, title='Star Wars: Episode IV - A New Hope', rating=10),
        *get_films_to_load(1, title='All the stars in the universe', rating=7),
    ]
    endpoint = ENDPOINT_SEARCH

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, query_params)

    assert response['status'] == expected_response['status']
    assert len(response['body']) == expected_response['length']
    if expected_response['status'] == HTTPStatus.NOT_FOUND:
        assert response['body'] == {'detail': 'Films not found'}
    if expected_response['status'] == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert response['body']['detail'][0]['type'] == 'string_too_short'


async def test_film_search_fields(
        es_load,
        make_get_request,
):
    """Check the correctness and completeness of the data return."""

    film_data_in = [
        *get_films_to_load(2, title='film 1', rating=10),
        *get_films_to_load(1, title='film 1', rating=8),
        *get_films_to_load(1, title='film 2', rating=10),
        *get_films_to_load(1, title='film 3', rating=7),
    ]
    endpoint = ENDPOINT_SEARCH

    target_title = 'film 1'
    target_rating = 10
    query_params = {'query': 'film'}

    target_item = [film for film in film_data_in
                   if film['title'] == target_title and film['imdb_rating'] == target_rating]

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, query_params)

    response_item = [film for film in response['body']
                     if film['title'] == target_title and film['imdb_rating'] == target_rating]

    assert len(response['body']) == len(film_data_in)
    assert response_item == target_item
    assert response['status'] == HTTPStatus.OK


@pytest.mark.parametrize(
    'params, expected_order',
    [
        (
                {'query': 'stars'},
                {
                    'status': HTTPStatus.OK,
                    'order': [
                        'All the stars in the universe',
                        'Star Wars. Episode I: The Phantom Menace',
                        'Star Wars: Episode IV - A New Hope'
                    ],
                },
        ),
        (
                {'query': 'wars'},
                {
                    'status': HTTPStatus.OK,
                    'order': [
                        'Star Wars. Episode I: The Phantom Menace',
                        'Star Wars: Episode IV - A New Hope'
                    ],
                },
        ),
        (
                {'query': 'star wars'},
                {
                    'status': HTTPStatus.OK,
                    'order': [
                        'Star Wars. Episode I: The Phantom Menace',
                        'Star Wars: Episode IV - A New Hope',
                        'All the stars in the universe'
                    ],
                },
        ),
        (
                {'query': 'SUPERSTAR'},
                {'status': HTTPStatus.OK, 'order': ['Talking to a superstar']},
        ),
    ],
)
async def test_film_search_relevance(
        es_load, make_get_request, params, expected_order
):
    """Check the sorting and filtering parameters by genre."""

    film_data_in = [
        *get_films_to_load(1, title='Star Wars. Episode I: The Phantom Menace', rating=4),
        *get_films_to_load(1, title='Talking to a superstar', rating=10),
        *get_films_to_load(1, title='Starving', rating=8),
        *get_films_to_load(1, title='Star Wars: Episode IV - A New Hope', rating=10),
        *get_films_to_load(1, title='All the stars in the universe', rating=7),
    ]
    endpoint = ENDPOINT_SEARCH

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)
    received_order = [item['title'] for item in response['body']]

    assert response['status'] == expected_order['status']
    assert received_order == expected_order['order']


@pytest.mark.parametrize(
    'params, expected_order',
    [
        (
                {'sort': '-imdb_rating'},
                {'status': HTTPStatus.OK, 'order': ['film 2', 'film 5', 'film 4'],
                 },
        ),
        (
                {},  # Sorting is not set, i.e. it sorts by relevance.
                {'status': HTTPStatus.OK, 'order': ['film 5', 'film 4', 'film 2']},
        ),
        (
                {'sort': 'imdb_rating'},
                {'status': HTTPStatus.OK, 'order': ['film 4', 'film 5', 'film 2'],
                 },
        ),
        (
                {'sort': '-imdb_rating', 'genre_name': 'Action'},
                {'status': HTTPStatus.OK, 'order': ['film 5', 'film 4']},
        ),
        (
                {'sort': 'imdb_rating', 'genre_name': 'Action'},
                {'status': HTTPStatus.OK, 'order': ['film 4', 'film 5']},
        ),
        (
                {'genre_name': 'Action'},
                {'status': HTTPStatus.OK, 'order': ['film 5', 'film 4']},
        ),
        (
                {'sort': 'imdb_rating', 'genre_name': 'Non-existent Genre'},
                {'status': HTTPStatus.NOT_FOUND, 'order': None},
        ),
    ],
)
async def test_film_search_sort_genre(
        es_load, make_get_request, params, expected_order
):
    """Check the sorting and filtering parameters by genre for the fuzzy search."""

    film_data_in = [v for v in film_to_load.values()]

    endpoint = ENDPOINT_SEARCH
    params |= {'query': 'film 5'}

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response['status'] == expected_order['status']
    received_order = (
        [FILM[f['uuid']] for f in response['body']]
        if response['status'] == HTTPStatus.OK
        else None
    )
    assert received_order == expected_order['order']


    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response['status'] == expected_order['status']
    received_order = (
        [FILM[f['uuid']] for f in response['body']]
        if response['status'] == HTTPStatus.OK
        else None
    )

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

    film_data_in = get_films_to_load(75)
    endpoint = ENDPOINT_SEARCH
    params = page_params | {'query': 'film'}

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response['status'] == expected_response['status']
    assert len(response["body"]) == expected_response['length']


async def test_film_search_cache(
        es_load,
        make_get_request,
        redis_client: Redis,
):
    """Checking the operation of the cache for the fuzzy search."""

    number = 75
    film_data_in = get_films_to_load(number)
    endpoint = ENDPOINT_SEARCH
    page_number = 2
    page_size = 50
    params = {'query': 'film', 'page_number': page_number, 'page_size': page_size}
    length_films = number - page_size

    # 1) Загружаем данные в эластик
    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert len(response['body']) == length_films

    # 2) Подгружаем еще фильмы и отправляем запрос с теми же параметрами
    add_number = 10
    film_data_in = get_films_to_load(add_number)
    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)
    # Проверяем, что кэш работает - вернулось старое количество фильмов из кэша
    assert len(response['body']) == length_films

    # 3) Сбрасываем кэш. Теперь возвращается количество с учетом добавленных фильмов
    await redis_client.flushall()
    response = await make_get_request(endpoint, params)

    assert len(response['body']) == length_films + add_number
