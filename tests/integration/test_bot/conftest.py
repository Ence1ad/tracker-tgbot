from typing import Any

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import User, Chat

from cache.trackers_redis_manager import redis_hmset_create_tracker
from config import settings
from tests.integration.mocked_bot import MockedBot
from tests.integration.test_bot.utils import get_update, get_callback_query, \
    get_message, TEST_CHAT
from tests.utils import TRACKER_ID, ACTION_NAME, ACTION_ID, CATEGORY_NAME, CATEGORY_ID
from tgbot.__main__ import _register_middlewares, _register_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.schedule.schedule_adjustment import setup_scheduler


@pytest_asyncio.fixture(scope='class')
async def redis_storage(redis_url):
    if not redis_url:
        pytest.skip("Redis is not available here")
    storage = RedisStorage.from_url(redis_url)
    try:
        await storage.redis.info()
    except ConnectionError as e:
        pytest.skip(str(e))
    try:
        yield storage
    finally:
        conn = await storage.redis
        await conn.flushdb()
        await storage.close()


@pytest_asyncio.fixture()
async def bot():
    return MockedBot()


@pytest.fixture()
def i18n(lang_bot_settings):
    hub = Translator()
    return hub.t_hub.get_translator_by_locale(lang_bot_settings)


@pytest.fixture()
def buttons():
    return AppButtons()


@pytest_asyncio.fixture()
async def scheduler(async_session_fixture, redis_storage, bot, redis_cli):
    schedule = await setup_scheduler(
        bot=bot, jobstores=settings.scheduler_job_stores, redis_client=redis_cli,
        storage=redis_storage, async_session=async_session_fixture
    )
    return schedule


@pytest_asyncio.fixture()
async def dispatcher(bot, redis_cli, buttons, lang_bot_settings, async_session_fixture,
                     redis_storage, scheduler):

    dp = Dispatcher(storage=redis_storage)
    translator = Translator(global_lang=lang_bot_settings)

    await _register_middlewares(
        dp=dp, async_session=async_session_fixture, buttons=buttons,
        redis_client=redis_cli, translator=translator, scheduler=scheduler,
        throttling=(35, 30)
    )
    await _register_handlers(dp)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await bot.session.close()
        await dp.emit_shutdown()


@pytest_asyncio.fixture()
async def execute_callback_query_handler(bot: MockedBot, dispatcher: Dispatcher,
                                         chat_fixt_fact):
    async def get_handler_result(user_id: int, data, state=None):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        chat: Chat = await chat_fixt_fact(user_id)
        if state is not None:
            context = dispatcher.fsm.get_context(bot=bot, chat_id=chat.id,
                                                 user_id=user.id)
            await context.set_state(state)
        res = await dispatcher.feed_update(bot=bot, update=get_update(
            callback_query=get_callback_query(data=data, from_user=user))
                                           )
        return res
    return get_handler_result


@pytest_asyncio.fixture()
async def execute_message_handler(bot: MockedBot, dispatcher: Dispatcher,
                                  chat_fixt_fact):
    async def get_handler_result(user_id: int, text, state=None):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        chat: Chat = await chat_fixt_fact(user_id)
        if state is not None:
            context = dispatcher.fsm.get_context(bot=bot, chat_id=chat.id,
                                                 user_id=user.id)
            await context.set_state(state)

        res = await dispatcher.feed_update(bot=bot, update=get_update(
            message=get_message(text=text, chat=chat, from_user=user))
                                           )
        return res
    return get_handler_result


@pytest_asyncio.fixture
async def create_tracker_fixt_fact(redis_cli):
    async def _create_tracker_fixt_fact(
            user_id: int, category_id: int = CATEGORY_ID,
            category_name: str = CATEGORY_NAME, action_id: int = ACTION_ID,
            action_name: str = ACTION_NAME, tracker_id: str = TRACKER_ID
    ) -> Any | None:
        tracker = await redis_hmset_create_tracker(
            user_id=user_id, tracker_id=tracker_id, action_id=action_id,
            action_name=action_name, category_id=category_id,
            category_name=category_name, redis_client=redis_cli
        )
        return tracker
    return _create_tracker_fixt_fact


@pytest_asyncio.fixture
async def chat_fixt_fact():
    async def _create_chat(
            chat_id: int = None, chat_type: str = 'private', title: str = 'TEST_TITLE',
            username: str = TEST_CHAT.username, **kwargs
    ) -> Chat:
        return Chat(id=chat_id, type=chat_type, title=title, username=username,
                    **kwargs)
    return _create_chat


@pytest_asyncio.fixture
async def set_state_data_fict_fact(chat_fixt_fact, dispatcher, bot):
    async def set_state_data(user_id, data):
        chat: Chat = await chat_fixt_fact(user_id)
        key = StorageKey(bot_id=bot.id, chat_id=chat.id, user_id=user_id)
        return await dispatcher.fsm.storage.set_data(key=key, data=data)
    return set_state_data


@pytest_asyncio.fixture
async def get_state_fict_fact(chat_fixt_fact, dispatcher, bot):
    async def get_state(user_id):
        chat: Chat = await chat_fixt_fact(user_id)
        key = StorageKey(bot_id=bot.id, chat_id=chat.id, user_id=user_id)
        state = await dispatcher.fsm.storage.get_state(key)
        return state
    return get_state
