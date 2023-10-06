import asyncio
import sys

import pytest
import pytest_asyncio
import redis.asyncio as redis
import sqlalchemy as sa
from redis.asyncio import Redis
from sqlalchemy import Result
from sqlalchemy import text, make_url, URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from config import settings
from db import UserModel
from db.actions.actions_db_commands import create_actions
from db.base_model import AsyncSaBase
from db.categories.categories_commands import create_category
from db.tracker.tracker_db_command import create_tracker
from db.users.users_commands import create_user
from tgbot.tests.utils import MAIN_USER_ID, ACTION_NAME, CATEGORY_NAME, \
    SECOND_USER_ID, USER_ID_WITH_TRACKER_LIMIT


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
        help="run tests which require redis connection"
    )

    parser.addoption(
        "--lang",
        default=None,
        help="run bot tests with lang_code user settings"
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
        username='postgres',
        host='localhost',
        port=5432,
        database='new'
    ).render_as_string()
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
    async with async_sqlalchemy_engine.begin() as conn:
        async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            async_sqlalchemy_engine, class_=AsyncSession, expire_on_commit=False)
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


@pytest_asyncio.fixture(scope='class')
async def db_user_factory(db_session: async_sessionmaker[AsyncSession]):
    async def _db_user_factory(user_id):
        async with db_session as db_sess:
            stmt: Result = await db_sess.execute(sa.select(UserModel).where(UserModel.user_id == user_id))
            user = stmt.scalar_one_or_none()
        if user is None:
            user_obj = await create_user(user_id=user_id, first_name='', last_name='', username='',
                                         db_session=db_session)
            return user_obj.user_id
    return _db_user_factory


@pytest_asyncio.fixture(scope='class')
async def db_category_factory(db_user_factory, db_session: async_sessionmaker[AsyncSession]):
    async def _db_category_factory(user_id, category_name: str = CATEGORY_NAME):
        await db_user_factory(user_id)
        try:
            category_obj = await create_category(user_id=user_id, category_name=category_name, db_session=db_session)
            return category_obj
        except IntegrityError as ex:
            return
    return _db_category_factory


@pytest_asyncio.fixture(scope="class")
async def add_data_to_db(db_user_factory, db_category_factory,  db_session,):
    users = [MAIN_USER_ID, SECOND_USER_ID, USER_ID_WITH_TRACKER_LIMIT]

    tracker_obj = None
    for user_id in users:

        user_id = await db_user_factory(user_id=user_id)
        category_obj = await db_category_factory(user_id)
        category_id = category_obj.category_id
        action_obj = await create_actions(user_id=user_id, action_name=ACTION_NAME,
                                          category_id=category_id, db_session=db_session)
        tracker_obj = await create_tracker(user_id=user_id, category_id=category_id,
                                           action_id=action_obj.action_id, db_session=db_session)
    yield tracker_obj
