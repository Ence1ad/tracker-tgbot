from contextlib import nullcontext as does_not_raise

import pytest
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.methods import SendMessage, EditMessageText
from aiogram.types import User
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db.categories.categories_commands import select_categories
from tests.unit_tests.mocked_bot import MockedBot
from tests.unit_tests.test_bot.utils import TEST_USER, get_update, get_callback_query, get_message
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import new_user_text, empty_categories_text, added_new_category_text, select_category_text


@pytest.mark.parametrize(
    "user_id, data, answer_text, expectation",
    [
        (TEST_USER.id, AppButtons.categories_data.CREATE_CATEGORIES.name, new_user_text, does_not_raise()),
    ]
)
@pytest.mark.asyncio
async def test_prompt_new_category_handler(user_id: int, answer_text: str, data: str, expectation: does_not_raise,
                                           dispatcher: Dispatcher, bot: MockedBot, bot_db_session: async_sessionmaker[AsyncSession], redis_cli: Redis):
    res: FSMContext = await dispatcher.feed_update(bot=bot, update=get_update(callback_query=get_callback_query(data=data)))
    with expectation:
        assert isinstance(res, FSMContext)
        assert await res.get_data() == {}
        assert isinstance(res.storage, RedisStorage)


@pytest.mark.parametrize(
    "user_id, data, text, expectation",
    [
        (TEST_USER.id, 'categories_btn', empty_categories_text, does_not_raise()),
    ]
)
@pytest.mark.asyncio
async def test_display_categories(user_id: int, text: str, data: str, expectation: does_not_raise,
                                  dispatcher: Dispatcher, bot: MockedBot, bot_db_session: async_sessionmaker[AsyncSession], buttons: AppButtons):
    res = await dispatcher.feed_update(bot=bot, update=get_update(callback_query=get_callback_query(data=data)))
    with expectation:
        assert isinstance(res, SendMessage)
        assert res.text == text
        assert res.reply_markup == await menu_inline_kb(await buttons.new_category())


@pytest.mark.parametrize(
    "user_id, new_category_name, answer_text, expectation",
    [
        (TEST_USER.id, 'Anki_category', added_new_category_text, does_not_raise()),
    ]
)
@pytest.mark.asyncio
async def test_create_category_handler(
        user_id: int, answer_text: str, new_category_name: str, expectation: does_not_raise, dispatcher: Dispatcher, bot: MockedBot,
        bot_db_session: async_sessionmaker[AsyncSession], buttons: AppButtons
):
    res: SendMessage = await dispatcher.feed_update(bot=bot, update=get_update(message=get_message(text=new_category_name)))
    with expectation:
        assert isinstance(res, SendMessage)
        assert res.text == answer_text
        assert res.reply_markup == await menu_inline_kb(await buttons.category_menu_buttons())
        res_from_db = await select_categories(user_id, bot_db_session())
        assert res_from_db[0].category_name == new_category_name
        # checking that state was successfully clean
        state = await dispatcher.fsm.storage.get_data(StorageKey(bot_id=42, chat_id=12, user_id=1111111111,
                                                                 thread_id=None, destiny='default'))
        assert state == {}


@pytest.mark.parametrize(
    "user_id, data, answer_text, expectation",
    [
        (TEST_USER.id, AppButtons.categories_data.DELETE_CATEGORIES.name, select_category_text, does_not_raise()),
        (123, 'delete_categories', empty_categories_text, does_not_raise()),
    ]
)
@pytest.mark.asyncio
async def test_pick_removing_category_handler(
        user_id: int, answer_text: str, data: str,
        expectation: does_not_raise, dispatcher: Dispatcher, bot: MockedBot,
):
    user = User(id=user_id, is_bot=False, first_name='')
    res = await dispatcher.feed_update(
        bot=bot,
        update=get_update(callback_query=get_callback_query(data=data, from_user=user))
    )
    with expectation:
        assert isinstance(res, EditMessageText)
        assert res.text == answer_text
