import asyncio
import sys

import pytest
import pytest_asyncio
from redis import asyncio as redis
from redis.asyncio import Redis
from sqlalchemy import URL, make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, \
    async_sessionmaker, AsyncSession

from config import settings
from db.base_model import AsyncSaBase


def pytest_addoption(parser):
    """
    Add custom command-line options for pytest configuration.

    This function allows you to define custom command-line options that can be used
    to configure pytest behavior for your tests. The function adds options for
    specifying<database and Redis connection URLs, as well as language settings.

    Command-line options:
    --db-url: Use the given Postgres URL for the connection to the test database.
    --redis: Use the given Redis URL for the connection to the test Redis database.
    --lang: Use the given language code to configure and run bot tests.

    Example usage:
    pytest --db-url="postgresql://user:password@localhost:5432/test_db" \
    --redis="redis://localhost:6379/0" --lang="en_US"

    :param parser: The pytest command-line argument parser.
    :return: None
    """
    parser.addoption(
        "--db-url",
        action="store",
        default="",
        help="Use the given Postgres URL for the connection to test_db",
    )

    parser.addoption(
        "--redis",
        default=None,
        help="Use the given Redis URL for the connection to test_redis_db"
    )

    parser.addoption(
        "--lang",
        default=None,
        help="Use the given lang_code and run bot tests"
    )


@pytest.fixture(scope="session")
def event_loop():
    """
    Fixture providing an asyncio event loop for test sessions.

    This fixture creates and yields an asyncio event loop suitable for running
    asynchronous tests. It also ensures that the event loop policy is set correctly for
    Windows systems using Python 3.8 or higher.

    :return: asyncio.AbstractEventLoop: An asyncio event loop for running asynchronous tests.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def redis_url(request):
    """
    Fixture providing the Redis URL for test Redis database connection.

    This fixture retrieves the Redis URL from command-line options or a session
    fixture. If the URL is not provided, it falls back to the default Redis URL.
    Use the `--redis` option or define a "_redis_url" session fixture to specify
    the URL.

    :param request: The pytest request object.
    :return: str: The Redis URL for the test Redis database connection.
    """
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
    """
    Fixture providing the default Redis URL for test Redis database connection.

    This fixture defines the default Redis URL used for connecting to the test Redis
    database. It includes the necessary connection details, such as host, port, and
    authentication.

    :return: str: The default Redis URL for the test Redis database connection.
    """
    url = f"redis://:{settings.REDIS_PASSWORD}@localhost:{settings.REDIS_PORT}/11?protocol=3"
    return url


@pytest.fixture(scope="session")
def database_url(request):
    """
    Fixture providing the database URL for test database connection.

    This fixture retrieves the database URL from command-line options or a session
    fixture. If the URL is not provided, it falls back to the default database URL.
    Use the `--db-url` option or define a "_database_url" session fixture to specify
    the URL.

    :param request: The pytest request object.
    :return: str: The database URL for the test database connection.
    """
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
    """
    Fixture providing the language code for bot tests.

    This fixture retrieves the language code from command-line options or a session
    fixture. If the language code is not provided, it falls back to the default
    language code. Use the `--lang` option or define a "_lang_bot_settings" session
    fixture to specify the code.

    :param request: The pytest request object.
    :return: str: The language code for configuring and running bot tests.
    """
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
    """
    Fixture providing the default language code for bot tests.

    This fixture defines the default language code used for configuring and running bot
    tests.

    :return: str: The default language code for bot tests.
    """
    return settings.GLOBAL_LANG_CODE


POSTGRES_DEFAULT_DB = "postgres"


@pytest_asyncio.fixture(scope="session")
async def _database_url():
    """
    Fixture providing the database URL for the test database connection.

    This fixture constructs the database URL using configuration settings and returns
    it. The URL is used to connect to the PostgreSQL test database.

    :return: str: The constructed database URL.
    """
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host='localhost',
        port=settings.POSTGRES_PORT,
        database='test_db'
    ).render_as_string(hide_password=False)
    return url


@pytest_asyncio.fixture(scope='session')
async def redis_cli(redis_url):
    """
    Fixture providing an asynchronous Redis client.

    This fixture creates an asynchronous Redis client using the specified Redis URL.
    The client is used for interacting with the Redis database during tests.

    :param redis_url: str: The Redis URL for connecting to the Redis database.
    :return: redis.asyncio: An asynchronous Redis client.
    """
    redis_client: Redis = redis.from_url(redis_url)
    async with redis_client as conn:
        yield conn
        await conn.flushdb()


@pytest_asyncio.fixture(scope="session")
async def setup_database(database_url, event_loop):
    """
    Fixture for setting up the test database.

    This fixture creates and configures the test database using the provided database
    URL. It also handles cleanup after tests by dropping the test database.

    :param database_url: str: The database URL for the test database.
    :param event_loop: The asyncio event loop.
    :return: str: The database URL.
    """
    await create_database(database_url)
    try:
        yield database_url
    finally:
        await drop_database(database_url)


@pytest_asyncio.fixture(scope="session")
async def async_sqlalchemy_engine(setup_database):
    """
    Fixture providing an asynchronous SQLAlchemy engine for the test database.

    This fixture creates an asynchronous SQLAlchemy engine using the database URL
    obtained from the `setup_database` fixture. The engine is used for database
    interaction in tests.

    :param setup_database: str: The database URL for the test database.
    :return: sqlalchemy.ext.asyncio.AsyncEngine: An asynchronous SQLAlchemy engine.
    """
    engine: AsyncEngine = create_async_engine(setup_database)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def create_drop_models(async_sqlalchemy_engine):
    """
    Fixture for creating and dropping database models.

    This fixture creates database models using SQLAlchemy. It runs the `create_all`
    method to create the database schema at the beginning of the test module and then
    drops the schema at the end of the module.

    :param async_sqlalchemy_engine: The asynchronous SQLAlchemy engine.
    :return: None
    """
    async with async_sqlalchemy_engine.begin() as conn:
        await conn.run_sync(AsyncSaBase.metadata.create_all)
    yield
    async with async_sqlalchemy_engine.begin() as conn:
        await conn.run_sync(AsyncSaBase.metadata.drop_all)


@pytest_asyncio.fixture(scope='class')
async def async_session_fixture(async_sqlalchemy_engine):
    """
    Fixture providing an asynchronous SQLAlchemy session.

    This fixture creates an asynchronous SQLAlchemy session for the test database.
    The session is used for performing database operations during class-level tests.

    :param async_sqlalchemy_engine: The asynchronous SQLAlchemy engine.
    :return: sqlalchemy.ext.asyncio.AsyncSession: An asynchronous SQLAlchemy session.
    """
    async with async_sqlalchemy_engine.begin():
        async_session = async_sessionmaker(async_sqlalchemy_engine, class_=AsyncSession,
                                           expire_on_commit=False)
        yield async_session


@pytest_asyncio.fixture(scope='class')
async def db_session_fixture(async_session_fixture):
    """
    Fixture providing an asynchronous database session.

    This fixture creates an asynchronous database session using the
    `async_session_fixture`. The session is used for performing database operations
    during class-level tests.

    :param async_session_fixture: The asynchronous SQLAlchemy session fixture.
    :return: An asynchronous database session.
    """
    async with async_session_fixture() as db_session:
        yield db_session


async def create_database(url: str):
    """
    Create a new database in the PostgreSQL server.

    This function is used to create a new PostgreSQL database using the specified URL.
    It checks if the database already exists and, if not, creates the new database.

    :param url: The database URL.
    :return: None
    """
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
    """
    Drop a database from the PostgreSQL server.

    This function is used to drop a PostgreSQL database based on the specified URL.
    It disconnects users and drops the database.

    :param url: The database URL.
    :return: None
    """
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
