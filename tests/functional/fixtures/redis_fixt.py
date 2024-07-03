from typing import AsyncGenerator

import pytest
from redis.asyncio import Redis

from functional.settings import test_settings


@pytest.fixture(scope="session")
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Создаем клиента для работы с Redis. В конце закрываем его."""

    client = Redis.from_url(test_settings.redis_dsn)
    yield client
    await client.aclose()

@pytest.fixture(autouse=True)
async def redis_clear_cache(redis_client: Redis) -> None:
    """Сбрасываем кэш"""

    await redis_client.flushall()
