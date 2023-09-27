import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import User
from cache.redis_language_commands import LANG_CODE
from config import settings
from tests.unit_tests.mocked_bot import MockedBot
from tests.unit_tests.test_bot.utils import get_update, get_callback_query, get_message, TEST_CHAT
from tgbot.handlers import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.middlewares import DbSessionMiddleware, CacheMiddleware, SchedulerMiddleware
from tgbot.middlewares.button_middleware import ButtonsMiddleware
from tgbot.middlewares.translation_middleware import TranslatorRunnerMiddleware
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
def i18n():
    hub = Translator()
    return hub.t_hub.get_translator_by_locale(LANG_CODE)


@pytest.fixture()
def buttons():
    return AppButtons()

@pytest_asyncio.fixture()
async def scheduler(async_session, redis_storage, bot, redis_cli):
    schedule = await setup_scheduler(bot=bot, jobstores=settings.scheduler_job_stores, redis_client=redis_cli,
                                      storage=redis_storage, async_session=async_session,
                                      # t_hub=translator.t_hub
                                      )
    return schedule

@pytest_asyncio.fixture()
async def dispatcher(bot, redis_cli, buttons, i18n, async_session,  redis_storage, scheduler):
    dp = Dispatcher(storage=redis_storage)
    translator = Translator()

    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(CacheMiddleware(redis_cli))
    dp.callback_query.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(ButtonsMiddleware(buttons))
    dp.update.middleware.register(TranslatorRunnerMiddleware(translator.t_hub))

    common_handlers_router = register_common_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    actions_router = register_actions_handlers()
    report_router = register_report_handlers()
    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await bot.session.close()
        await dp.emit_shutdown()


@pytest_asyncio.fixture()
async def execute_callback_query_handler(bot: MockedBot, dispatcher: Dispatcher):
    async def get_handler_result(user_id: int, data, state=None):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        if state is not None:
            context = dispatcher.fsm.get_context(bot=bot, chat_id=TEST_CHAT.id, user_id=user.id)
            await context.set_state(state)
        res = await dispatcher.feed_update(bot=bot, update=get_update(callback_query=get_callback_query(data=data,
                                                                                                        from_user=user)))
        return res
    return get_handler_result


@pytest_asyncio.fixture()
async def execute_message_handler(bot: MockedBot, dispatcher: Dispatcher):
    async def get_handler_result(user_id: int, text, state=None):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        if state is not None:
            context = dispatcher.fsm.get_context(bot=bot, chat_id=TEST_CHAT.id, user_id=user.id)
            await context.set_state(state)

        res = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text=text, from_user=user)))
        return res
    return get_handler_result

