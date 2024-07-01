import asyncio
from typing import Any, AsyncGenerator, Callable, Coroutine

import pytest
from aiohttp import ClientSession

from functional.settings import test_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop."""

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def a_client() -> AsyncGenerator[ClientSession, None]:
    """
    Get a client for making http requests.
    At the end, we close it.
    """

    client = ClientSession()
    yield client
    await client.close()


@pytest.fixture
def make_get_request(
    a_client: ClientSession,
) -> Callable[[str, dict | None], Coroutine[Any, Any, dict[str, Any]]]:
    """
    Make a GET request to a specific endpoint by passing parameters.
    Get the response.
    """

    async def inner(
        endpoint: str, params: dict | None = None
    ) -> dict[str, Any]:
        params = params or {}
        url = f"{test_settings.app_url}{endpoint}"
        async with a_client.get(url=url, params=params) as resp:
            return {
                "body": await resp.json(),
                "status": resp.status,
                "headers": resp.headers,
                "url": resp.url,
            }

    return inner

# TODO make fixt for POST request
