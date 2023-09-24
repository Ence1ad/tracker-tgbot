import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import User
from sqlalchemy import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import sqlalchemy as sa
from cache.redis_language_commands import LANG_CODE
from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_delete_tracker
from config import settings
from db import UserModel, CategoriesModel
from db.categories.categories_commands import create_category, delete_category
from db.users.users_commands import create_user
from tests.unit_tests.mocked_bot import MockedBot
from tests.unit_tests.test_bot.utils import USER_ID, LANG_CODE, get_update, get_callback_query, get_message, TEST_CHAT
from tgbot.handlers import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.middlewares import DbSessionMiddleware, CacheMiddleware
from tgbot.middlewares.button_middleware import ButtonsMiddleware
from tgbot.middlewares.translation_middleware import TranslatorRunnerMiddleware


TRACKER_ID = str(1)
ACTION_ID = 1
ACTION_NAME = 'action_test'
CATEGORY_ID = 1
CATEGORY_NAME = 'category_test'


@pytest_asyncio.fixture
async def create_tg_user():  # fixture factory
    async def _create_tg_user(user_id, first_name='test_name', is_bot=False, lang_code=LANG_CODE):
        return User(id=user_id, first_name=first_name, is_bot=is_bot, language_code=lang_code)
    return _create_tg_user


@pytest_asyncio.fixture
async def get_tracker(redis_cli):
    tracker = await redis_hmset_create_tracker(
        user_id=USER_ID, tracker_id=TRACKER_ID, action_id=ACTION_ID, action_name=ACTION_NAME,
        category_id=CATEGORY_ID, category_name=CATEGORY_NAME, redis_client=redis_cli)
    yield tracker
    await redis_delete_tracker(user_id=USER_ID, redis_client=redis_cli)


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


# @pytest_asyncio.fixture(scope="class")
# async def db_user(db_session: async_sessionmaker[AsyncSession]):
#     async with db_session as db_sess:
#         stmt: Result = await db_sess.execute(sa.select(UserModel).where(UserModel.user_id == USER_ID))
#         user = stmt.scalar_one_or_none()
#     if user is None:
#         user_obj = await create_user(user_id=USER_ID, first_name='', last_name='', username='',
#                                      db_session=db_session)
#         yield user_obj.user_id
#         async with db_session as db_sess:
#             await db_sess.execute(sa.delete(UserModel).where(UserModel.user_id == USER_ID))


@pytest_asyncio.fixture(scope="class")
async def create_categories_more_than_limit(db_user_factory, db_session: async_sessionmaker[AsyncSession]):
    await db_user_factory(USER_ID)
    for name in range(settings.USER_CATEGORIES_LIMIT):
        # async with db_session as db_sess:
        #     new_cat = CategoriesModel(user_id=db_user, category_name=str(name))
        #     db_sess.add(new_cat)
        await create_category(user_id=USER_ID, category_name=str(name), db_session=db_session)
    try:
        yield
    finally:
        for cat_id in range(settings.USER_CATEGORIES_LIMIT):
            await delete_category(user_id=USER_ID, category_id=cat_id+1, db_session=db_session)
                # async with db_session as db_sess:
                #     await db_sess.execute(sa.delete(CategoriesModel).where(CategoriesModel.category_id == cat_id+1))


@pytest_asyncio.fixture(scope='session')
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


@pytest.fixture()
def bot():
    return MockedBot()


@pytest.fixture()
def i18n():
    hub = Translator()
    return hub.t_hub.get_translator_by_locale(LANG_CODE)


@pytest_asyncio.fixture()
def buttons():
    return AppButtons()


@pytest_asyncio.fixture()
async def dispatcher(bot, redis_cli, buttons, i18n, async_sqlalchemy_engine, redis_storage):
    # storage = RedisStorage(redis=redis_cli)
    dp = Dispatcher(storage=redis_storage)
    translator = Translator()
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            async_sqlalchemy_engine, class_=AsyncSession, expire_on_commit=False)
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(CacheMiddleware(redis_cli))
    # dp.callback_query.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(ButtonsMiddleware(buttons))
    dp.update.middleware.register(TranslatorRunnerMiddleware(translator.t_hub))

    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()
    dp.include_routers(common_handlers_router,categories_router, actions_router, tracker_router, report_router)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest_asyncio.fixture()
async def execute_callback_query_handler(bot: MockedBot, dispatcher: Dispatcher):
    async def get_handler_result(user_id: int, data, state=None, **kwargs):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        res = await dispatcher.feed_update(
            bot=bot,
            update=get_update(callback_query=get_callback_query(data=data, from_user=user, **kwargs)))
        return res
    return get_handler_result


@pytest_asyncio.fixture()
async def execute_message_handler(bot: MockedBot, dispatcher: Dispatcher, redis_storage):
    async def get_handler_result(user_id: int, text, state=None):
        user: User = User(id=user_id, first_name='test_user', is_bot=False)
        if state is not None:
            context = FSMContext(
                storage=redis_storage,
                key=StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
            )
            await context.set_state(state)

        res = await dispatcher.feed_update(
            bot=bot,
            update=get_update(message=get_message(text=text, from_user=user)))
        return res
    return get_handler_result
