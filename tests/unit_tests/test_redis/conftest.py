import pytest_asyncio
from aiogram.fsm.storage import redis
from redis.asyncio import Redis, ConnectionPool


@pytest_asyncio.fixture(scope='session')
async def redis_cli():
    url = f"redis://:@localhost:6379/11"
    pool: ConnectionPool = redis.ConnectionPool(url)
    async with Redis(connection_pool=pool) as conn:
        yield conn
        await conn.flushdb()
    await conn.connection_pool.disconnect()


