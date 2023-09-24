import asyncio
import sys

import pytest
import pytest_asyncio
import redis.asyncio as redis
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from sqlalchemy import text, make_url, URL

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from db.base_model import AsyncSaBase


def pytest_addoption(parser):
    parser.addoption(
        "--db-url",
        action="store",
        default="",
        help="Use the given Postgres URL and skip Postgres container booting",
    )

    parser.addoption(
        "--redis",
        default=None,
        help="run tests which require redis connection")

@pytest.fixture(scope="session")
def redis_url(request):
    url = request.config.getoption("redis")
    if url:
        return url
    else:
        try:
            return request.getfixturevalue("_redis_url")
        except pytest.FixtureLookupError:
            pytest.exit(
                'Redis URL not given. Define a "_redis_url" session fixture or '
                'use the "--redis" in the command line.',
                returncode=1,
            )
@pytest.fixture(scope="session")
def _redis_url():
    url = "redis://localhost:6379/11?protocol=3"
    return url


@pytest.fixture(scope="session")
def database_url(request):
    url = request.config.getoption("db_url")
    if url:
        return url
    else:
        try:
            return request.getfixturevalue("_database_url")
        except pytest.FixtureLookupError:
            pytest.exit(
                'Database URL not given. Define a "_database_url" session fixture or '
                'use the "--db-url" in the command line.',
                returncode=1,
            )
# Запускается первой


@pytest.fixture(scope="session")
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


POSTGRES_DEFAULT_DB = "postgres"


@pytest_asyncio.fixture(scope='session')
async def redis_cli(redis_url):
    redis_client: Redis = redis.from_url(redis_url)
    # async with Redis(connection_pool=r.connection_pool) as conn:
    async with redis_client as conn:
        yield conn
        await conn.flushdb()
        # await conn.connection.disconnect()


@pytest_asyncio.fixture(scope="session")
async def _database_url():
    url = URL.create(
        drivername="postgresql+asyncpg",
        username='postgres',
        # password=settings.DB_USER_PASS,
        host='localhost',
        port=5432,
        database='new'
    ).render_as_string()
    return url
# 'postgresql+asyncpg://postgres@localhost:5432/new'


# Запускается второй
@pytest_asyncio.fixture(scope="session")
async def setup_database(database_url, event_loop):
    await create_database(database_url)
    try:
        yield database_url
    finally:
        await drop_database(database_url)


# Запускается третьей
@pytest_asyncio.fixture(scope="session")
async def async_sqlalchemy_engine(setup_database):
    engine = create_async_engine(setup_database)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def create_drop_models(async_sqlalchemy_engine):
    async with async_sqlalchemy_engine.begin() as conn:
        await conn.run_sync(AsyncSaBase.metadata.create_all)
    yield
    async with async_sqlalchemy_engine.begin() as conn:
        await conn.run_sync(AsyncSaBase.metadata.drop_all)

# Запускается четвертой
@pytest_asyncio.fixture(scope='class')
async def db_session(async_sqlalchemy_engine):
    async with async_sqlalchemy_engine.begin() as conn:
        async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            async_sqlalchemy_engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db_session:
            yield db_session


@pytest_asyncio.fixture(scope="package")
def set_user_id():
    user_id: int = 1111111111
    yield user_id
    del user_id


async def create_database(url: str):
    url_object = make_url(url)
    database_name = url_object.database
    dbms_url = url_object.set(database=POSTGRES_DEFAULT_DB)
    engine = create_async_engine(dbms_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        c = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        )
        database_exists = c.scalar() == 1

    if database_exists:
        await drop_database(url_object)

    async with engine.connect() as conn:
        await conn.execute(
            text(f'CREATE DATABASE "{database_name}"')
        )
    await engine.dispose()


async def drop_database(url: URL):
    url_object = make_url(url)
    dbms_url = url_object.set(database=POSTGRES_DEFAULT_DB)
    engine = create_async_engine(dbms_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disconnect_users = """
        SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '%(database)s'
          AND %(pid_column)s <> pg_backend_pid();
        """ % {
            "pid_column": "pid",
            "database": url_object.database,
        }
        await conn.execute(text(disconnect_users))

        await conn.execute(text(f'DROP DATABASE "{url_object.database}"'))
