from typing import AsyncGenerator

import pytest
from redis.asyncio import Redis

from functional.settings import test_settings


@pytest.fixture(scope="session")
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Create the client to work with Redis. At the end, we close it."""

    client = Redis.from_url(test_settings.redis_dsn)
    yield client
    await client.aclose()


@pytest.fixture(autouse=True)
async def redis_clear_cache(redis_client: Redis) -> None:
    """Reset the cache."""

    await redis_client.flushall()
