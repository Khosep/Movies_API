from copy import deepcopy
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.person_data import person_to_load

INDEX_NAME = IndexName.PERSONS.value
ENDPOINT_EXACT_SEARCH_BY_NAME = f'{test_settings.prefix}/{INDEX_NAME}/exact_search/name'


@pytest.mark.parametrize(
    'person_name, expected_response',
    [
        (
                {'full_name': 'John Knoll'},
                {'status': HTTPStatus.OK},
        ),
        (
                {'full_name': 'John Knolls'},
                {'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'full_name': ''},
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_person_details_status(
        es_load, make_get_request, person_name, expected_response
):
    """Check the success of the data return"""

    person_data_in = person_to_load
    endpoint = f'{ENDPOINT_EXACT_SEARCH_BY_NAME}/{person_name["full_name"]}'

    # load data to elastic
    await es_load(INDEX_NAME, person_data_in)

    response = await make_get_request(endpoint)

    assert response['status'] == expected_response['status']


async def test_person_details_fields(
        es_load,
        make_get_request,
):
    """Check the correctness and completeness of the data return."""

    person_data_in = person_to_load
    endpoint = f'{ENDPOINT_EXACT_SEARCH_BY_NAME}/{person_to_load[0]["full_name"]}'

    await es_load(INDEX_NAME, person_data_in)
    response = await make_get_request(endpoint)

    assert response['body'] == [person_to_load[0]]
    assert response['status'] == HTTPStatus.OK


async def test_person_details_cache(
        es_load,
        make_get_request,
        redis_client: Redis,
):
    """Check the cache operation."""

    person_data_in = deepcopy(person_to_load)
    endpoint = f'{ENDPOINT_EXACT_SEARCH_BY_NAME}/{person_to_load[0]["full_name"]}'
    person_name = person_data_in[0]['full_name']
    new_person_name = 'New Person Name'

    # 1) load data to elastic
    await es_load(INDEX_NAME, person_data_in)
    # make get request
    response = await make_get_request(endpoint)

    assert response['body'][0]['full_name'] == person_name

    # 2) Change the name of the person in the elastic document to 'new_person_name' (person_id is the same)
    person_data_in[0]['full_name'] = new_person_name
    await es_load(INDEX_NAME, person_data_in)

    # make the same request as in the first stage
    # (We are looking for the old name (in endpoint), although the name is already new)
    response = await make_get_request(endpoint)

    # Check that the cache is working - the old name ('person_name') has returned from the cache
    assert response['status'] == HTTPStatus.OK
    assert response['body'][0]['full_name'] == person_name

    # 3) Reset the redis cache.
    # Now the request (for old endpoint with the old name) will return 404 error
    await redis_client.flushall()
    response = await make_get_request(endpoint)

    assert response['body'] == {'detail': 'Persons not found'}
