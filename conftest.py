import asyncio
import sys

import pytest
import pytest_asyncio
from redis import asyncio as redis
from redis.asyncio import Redis
from sqlalchemy import URL, make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from config import settings
from db.base_model import AsyncSaBase


def pytest_addoption(parser):
    parser.addoption(
        "--db-url",
        action="store",
        default="",
        help="Use the given Postgres URL for the connection to test_db",
    )

    parser.addoption(
        "--redis",
        default="store",
        help="Use the given Redis URL for the connection to test_redis_db"
    )

    parser.addoption(
        "--lang",
        default=None,
        help="Use the given lang_code and run bot tests"
    )


@pytest.fixture(scope="session")
def event_loop():
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
    url = f"redis://:{settings.REDIS_PASSWORD}@localhost:6379/11?protocol=3"
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


@pytest.fixture(scope="session")
def lang_bot_settings(request):
    lang = request.config.getoption("lang")
    if lang:
        return lang
    else:
        try:
            return request.getfixturevalue("_lang_bot_settings")
        except pytest.FixtureLookupError:
            pytest.exit(
                'Lang code not given. Define a "_ru_bot_settings" session fixture or '
                'use the "--lang" in the command line.',
                returncode=1,
            )


@pytest.fixture(scope="session")
def _lang_bot_settings():
    return settings.GLOBAL_LANG_CODE


POSTGRES_DEFAULT_DB = "postgres"


@pytest_asyncio.fixture(scope='session')
async def redis_cli(redis_url):
    redis_client: Redis = redis.from_url(redis_url)
    async with redis_client as conn:
        yield conn
        await conn.flushdb()


@pytest_asyncio.fixture(scope="session")
async def _database_url():
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host='localhost',
        port=5432,
        database='test_db'
    ).render_as_string(hide_password=False)
    return url


@pytest_asyncio.fixture(scope="session")
async def setup_database(database_url, event_loop):
    await create_database(database_url)
    try:
        yield database_url
    finally:
        await drop_database(database_url)


@pytest_asyncio.fixture(scope="session")
async def async_sqlalchemy_engine(setup_database):
    engine:  AsyncEngine = create_async_engine(setup_database)
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


@pytest_asyncio.fixture(scope='class')
async def async_session(async_sqlalchemy_engine):
    async with async_sqlalchemy_engine.begin():
        async_session = async_sessionmaker(async_sqlalchemy_engine, class_=AsyncSession, expire_on_commit=False)
        yield async_session


@pytest_asyncio.fixture(scope='class')
async def db_session(async_session):
    async with async_session() as db_session:
        yield db_session


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
        SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database}'
          AND {pid_column} <> pg_backend_pid();
        """.format(
            pid_column="pid",
            database=url_object.database,
        )
        await conn.execute(text(disconnect_users))
        await conn.execute(text(f'DROP DATABASE "{url_object.database}"'))
