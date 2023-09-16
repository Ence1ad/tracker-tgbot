import pytest_asyncio
from redis.asyncio import Redis

from config import settings


@pytest_asyncio.fixture(scope='module')
async def redis_cli():
    if settings.TESTING:
        async with Redis(connection_pool=settings.create_redis_pool) as conn:
            yield conn
            await conn.flushdb()
        await conn.connection_pool.disconnect()

