import asyncio
import sys

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import User

from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from db.base_model import AsyncSaBase

from config import settings
from tests.unit_tests.mocked_bot import MockedBot
from tests.unit_tests.test_bot.utils import get_callback_query, get_update, get_message
from tgbot.handlers import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.middlewares import DbSessionMiddleware, CacheMiddleware, SchedulerMiddleware
from tgbot.middlewares.button_middleware import ButtonsMiddleware


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

@pytest.fixture(scope="package")
def async_engine():
    if settings.TESTING:
        engine = create_async_engine(
            settings.db_url
        )
        yield engine
        engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def create_drop_models(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncSaBase.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncSaBase.metadata.drop_all)


@pytest_asyncio.fixture(scope="class")
async def session(async_engine, create_drop_models):
    async with AsyncSession(async_engine) as db_session:
        yield db_session


@pytest_asyncio.fixture(scope="class")
async def bot_db_session(async_engine, create_drop_models):
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(async_engine, expire_on_commit=False,)
    yield async_session


@pytest_asyncio.fixture(scope='module')
async def redis_cli():
    if settings.TESTING:
        async with Redis(connection_pool=settings.create_redis_pool) as conn:
            yield conn
            await conn.flushdb()
        await conn.connection_pool.disconnect()


@pytest_asyncio.fixture(scope="package")
def set_user_id():
    user_id: int = 1111111111
    yield user_id
    del user_id


@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
def buttons():
    return AppButtons()

@pytest_asyncio.fixture()
async def dispatcher(bot, redis_cli, bot_db_session, buttons):
    storage = RedisStorage(redis=redis_cli)
    dp = Dispatcher(storage=storage)

    dp.update.middleware.register(DbSessionMiddleware(bot_db_session))
    dp.update.middleware.register(CacheMiddleware(redis_cli))
    # dp.callback_query.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(ButtonsMiddleware(buttons))

    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()
    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest_asyncio.fixture()
async def execute_callback_query_handler(bot: MockedBot, dispatcher: Dispatcher):
    async def get_handler_result(user_id: int, data):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        res = await dispatcher.feed_update(
            bot=bot,
            update=get_update(callback_query=get_callback_query(data=data, from_user=user)))
        return res
    return get_handler_result

@pytest_asyncio.fixture()
async def execute_message_handler(bot: MockedBot, dispatcher: Dispatcher):
    async def get_handler_result(user_id: int, command):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        res = await dispatcher.feed_update(
            bot=bot,
            update=get_update(message=get_message(text=command, from_user=user)))
        return res
    return get_handler_result
