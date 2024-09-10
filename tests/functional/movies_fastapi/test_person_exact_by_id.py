from copy import deepcopy
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName, test_settings
from functional.testdata.person_data import person_to_load

INDEX_NAME = IndexName.PERSONS.value
ENDPOINT_EXACT_SEARCH = f'{test_settings.prefix}/{INDEX_NAME}/exact_search'


@pytest.mark.parametrize(
    'person_uuid, expected_response',
    [
        (
                {'uuid': '1679c6cc-381b-4af5-ac0b-1172e422daaf'},
                {'status': HTTPStatus.OK},
        ),
        (
                {'uuid': '00000000-0000-0000-0000-000000000000'},
                {'status': HTTPStatus.NOT_FOUND},
        ),
        (
                {'uuid': 'Invalid UUID'},
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_person_details_status(
        es_load, make_get_request, person_uuid, expected_response
):
    """Check the success of the data return"""

    endpoint = f'{ENDPOINT_EXACT_SEARCH}/{person_uuid["uuid"]}'

    person_data_in = person_to_load
    # load data to elastic
    await es_load(INDEX_NAME, person_data_in)

    response = await make_get_request(endpoint)

    assert response['status'] == expected_response['status']


async def test_person_details_fields(
        es_load,
        make_get_request,
):
    """Check the correctness and completeness of the data return."""

    person_data_in = person_to_load[0]
    endpoint = f'{ENDPOINT_EXACT_SEARCH}/{person_data_in["uuid"]}'

    await es_load(INDEX_NAME, [person_data_in])
    response = await make_get_request(endpoint)

    print(f'\n {response["body"]=}')
    print(f'\n {person_to_load[0]=}')

    assert response['body'] == person_data_in
    assert response['status'] == HTTPStatus.OK


async def test_person_details_cache(
        es_load,
        make_get_request,
        redis_client: Redis,
):
    """Check the cache operation."""

    person_data_in = deepcopy(person_to_load[0])
    endpoint = f'{ENDPOINT_EXACT_SEARCH}/{person_data_in["uuid"]}'

    person_name = person_data_in['full_name']
    new_person_name = 'New Person Name'

    # 1) load data to elastic
    await es_load(INDEX_NAME, [person_data_in])
    # make get request
    response = await make_get_request(endpoint)

    assert response['body']['full_name'] == person_name

    # 2) Change the name of the person in the elastic document to 'new_person_name' (uuid is the same)
    person_data_in['full_name'] = new_person_name
    await es_load(INDEX_NAME, [person_data_in])

    # make the same request as in the first stage but with new full_name
    response = await make_get_request(endpoint)

    # Check that the cache is working - the old name ('person_name') has returned from the cache
    person_data_in['full_name'] = person_name

    # 3) Reset the redis cache. Now the current (new) person name is returned ('new_person_name')
    await redis_client.flushall()
    response = await make_get_request(endpoint)

    assert response['body']['full_name'] == new_person_name
