from contextlib import nullcontext as does_not_raise
from datetime import datetime
from enum import Enum

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.methods import SendMessage, EditMessageText
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache.redis_tracker_commands import redis_hmset_create_tracker, is_redis_hexists_tracker
from config import settings
from db.categories.categories_commands import select_categories
from tests.unit_tests.mocked_bot import MockedBot
from tests.unit_tests.test_bot.utils import TEST_CHAT
from tests.unit_tests.utils import MAIN_USER_ID
from tgbot.handlers.categories_handlers.read_categories import _categories_list
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryOperation, CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.states import CategoryState


@pytest.mark.usefixtures('create_categories_more_than_limit')
@pytest.mark.asyncio
class TestCategoriesHandlers:
    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.categories_data.CREATE_CATEGORIES.name, 'category_limit_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.categories_data.CREATE_CATEGORIES.name, 'new_category_text',
             pytest.raises(AssertionError)),
            (12345, AppButtons.categories_data.CREATE_CATEGORIES.name, 'new_category_text', does_not_raise()),
            (54321, AppButtons.categories_data.CREATE_CATEGORIES.name, '', pytest.raises(AssertionError)),
            (7000007, None, 'new_category_text', pytest.raises(AssertionError)),
            (333333, AppButtons.categories_data.DELETE_CATEGORIES.name, 'new_category_text',
             pytest.raises(AssertionError)),
        ]
    )
    async def test_prompt_new_category_handler(
            self, user_id: int, answer_text: str, data: str, expectation: does_not_raise,
            execute_callback_query_handler, db_user_factory,
            i18n: TranslatorRunner, buttons: AppButtons
    ):
        await db_user_factory(user_id)
        handler_returns: EditMessageText = await execute_callback_query_handler(user_id=user_id, data=data)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text, category_limit=settings.USER_CATEGORIES_LIMIT)
            if answer_text == 'category_limit_text':
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.category_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, new_category_name, answer_text, expectation",
        [
            (100001, CategoryState.GET_NAME, 'cat_name_from_user', 'added_new_category_text', does_not_raise()),
            (54321, CategoryState.GET_NAME, 'cat_name_from_user', 'added_new_category_text', does_not_raise()),
            (100001, CategoryState.GET_NAME, 'cat_name_from_user', 'category_exists_text', does_not_raise()),
            (100001, CategoryState.GET_NAME, 'cat_name_from_user', 'category_exists_text', does_not_raise()),
            (100001, CategoryState.GET_NAME, 'cat_name_from_user', 'added_new_category_text',
             pytest.raises(AssertionError)),
            (100001, CategoryState.GET_NAME, 'best_name', '', pytest.raises(AssertionError)),
            (100001, CategoryState.GET_NAME, '', 'added_new_category_text', pytest.raises(AssertionError)),
            (100001, CategoryState.GET_NAME, None, 'added_new_category_text', pytest.raises(AssertionError)),
            (100001, None, 'cat_name_from_user', 'added_new_category_text',
             pytest.raises(AssertionError)),
        ]
    )
    async def test_create_category_handler(
            self, user_id: int, new_category_name: str, state: FSMContext, expectation: does_not_raise,
            execute_message_handler, i18n: TranslatorRunner, bot, db_user_factory, answer_text: str,
            db_session: async_sessionmaker[AsyncSession], buttons: AppButtons, redis_storage):
        test_message = Message(message_id=1234, date=datetime.now(), chat=TEST_CHAT, text=new_category_name)
        await db_user_factory(user_id)
        handler_returns = await execute_message_handler(user_id=user_id, text=test_message.text, state=state)
        with expectation:
            state_data = await redis_storage.get_data(
                key=StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id))
            if not isinstance(new_category_name, str):
                assert handler_returns.text == i18n.get(answer_text, new_line='\n')
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
            elif state_data == {}:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
                assert new_category_name == (await select_categories(user_id, db_session))[0].category_name
                assert state_data == {}
            else:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == i18n.get(answer_text, new_category_name=new_category_name, new_line='\n')
                assert state_data['category_name'] == new_category_name

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (12345, AppButtons.general_data.CATEGORIES_BTN.name, 'empty_categories_text', does_not_raise()),
            (12345, AppButtons.general_data.CATEGORIES_BTN.name, 'show_categories_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.CATEGORIES_BTN.name, 'show_categories_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_data.CATEGORIES_BTN.name, 'empty_categories_text',
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.CATEGORIES_BTN.name, '', pytest.raises(AssertionError)),
            (12345, AppButtons.general_data.ACTIONS_BTN.name, 'empty_categories_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_display_categories(self, user_id: int, answer_text: str, data: str, expectation: does_not_raise,
                                      execute_callback_query_handler, i18n: TranslatorRunner, db_user_factory,
                                      db_session: async_sessionmaker[AsyncSession], buttons: AppButtons):
        handler_returns = await execute_callback_query_handler(user_id, data)
        with expectation:
            categories = await select_categories(user_id, db_session)
            columns_list_text = await _categories_list(categories)
            if categories:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == f"{i18n.get(answer_text)}\n\r{columns_list_text}"
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
            else:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.new_category(), i18n)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, cb_operation, expectation",
        [
            (MAIN_USER_ID, AppButtons.categories_data.DELETE_CATEGORIES.name, 'select_category_text', CategoryOperation.DEL,
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.categories_data.UPDATE_CATEGORIES.name, 'select_category_text', CategoryOperation.UPD,
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_data.ACTIONS_BTN.name, 'select_category_text', CategoryOperation.READ,
             does_not_raise()),
            (123, AppButtons.categories_data.DELETE_CATEGORIES.name, 'empty_categories_text', CategoryOperation.DEL,
             does_not_raise()),
            (123, AppButtons.categories_data.UPDATE_CATEGORIES.name, 'empty_categories_text', CategoryOperation.UPD,
             does_not_raise()),
            (123, AppButtons.general_data.ACTIONS_BTN.name, 'empty_categories_text', CategoryOperation.READ,
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.categories_data.CREATE_CATEGORIES.name, 'select_category_text', CategoryOperation.DEL,
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.categories_data.UPDATE_CATEGORIES.name, 'empty_categories_text', CategoryOperation.UPD,
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.ACTIONS_BTN.name, 'empty_categories_text', CategoryOperation.UPD,
             pytest.raises(AssertionError)),
        ]
    )
    async def test_get_categories(
            self, user_id: int, answer_text: str, data: str, expectation: does_not_raise,
            execute_callback_query_handler, buttons: AppButtons, i18n, cb_operation: Enum, db_session,
    ):
        handler_returns = await execute_callback_query_handler(user_id, data)
        with expectation:
            categories = await select_categories(user_id, db_session)
            if categories:
                assert isinstance(handler_returns, EditMessageText)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await callback_factories_kb(categories, cb_operation)
            else:
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.new_category(), i18n)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, CategoryCD(operation=CategoryOperation.UPD, category_id=2, category_name='cat_name'),
             'new_category_text',  does_not_raise()),
            (MAIN_USER_ID, CategoryCD(operation=CategoryOperation.UPD, category_id=2, category_name='cat_name'),
             'categories_is_fake_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, CategoryCD(operation=CategoryOperation.READ, category_id=1, category_name='1'),
             'new_category_text', pytest.raises(AssertionError)),
            (99999, CategoryCD(operation=CategoryOperation.UPD, category_id=0, category_name='0'),
             'new_category_text', does_not_raise()),
        ]
    )
    async def test_prompt_category_name(
            self,  user_id: int, answer_text: str, expectation: does_not_raise, execute_callback_query_handler,
            i18n, data: CategoryCD, redis_storage, bot
    ):
        handler_returns = await execute_callback_query_handler(user_id, data=data.pack())
        state_data = await redis_storage.get_data(key=StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id))
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text)
            assert state_data['category_id'] == data.category_id
            assert state_data['old_category_name'] == data.category_name

    @pytest.mark.parametrize(
        "user_id, state, old_category_name, new_category_name, answer_text, expectation",
        [
            (54321, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user', 'new_cat_name_from_user',
             'upd_category_text', does_not_raise()),
            (54321, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user', 'category_exists_text',
             'upd_category_text', does_not_raise()),
            (54321, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user', None, 'valid_category_name_text',
             does_not_raise()),
            (100001, CategoryState.WAIT_CATEGORY_DATA, None, 'new_cat_name_from_user', 'valid_data_text',
             does_not_raise()),
            (100001, CategoryState.GET_NAME, None, 'new_cat_name_from_user', 'valid_data_text',
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user', 'new_cat_name_from_user',
             'upd_category_text', pytest.raises(AssertionError))
        ]
    )
    async def test_upd_category_name(
            self, user_id: int, new_category_name: str, state: FSMContext, expectation: does_not_raise,
            execute_message_handler, i18n: TranslatorRunner, bot: MockedBot, answer_text: str,
            buttons: AppButtons, redis_storage: RedisStorage, old_category_name: str
    ):

        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        await redis_storage.set_data(key, data={"category_id": 1, 'old_category_name': old_category_name})
        test_message = Message(message_id=12345, date=datetime.now(), chat=TEST_CHAT, text=new_category_name)
        handler_returns = await execute_message_handler(user_id=user_id, text=test_message.text, state=state)
        with expectation:
            state_data = await redis_storage.get_data(key=key)

            assert isinstance(handler_returns, SendMessage)
            markup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
            assert state_data == {}
            if not isinstance(new_category_name, str):
                assert handler_returns.text == i18n.get(answer_text, new_line='\n')
                assert handler_returns.reply_markup == markup
            elif answer_text == 'category_exists_text':
                assert handler_returns.text == i18n.get(answer_text, new_category_name=new_category_name, new_line='\n')
                assert handler_returns.reply_markup == markup
            elif not old_category_name:
                assert handler_returns.text == i18n.get(answer_text)
            else:
                assert handler_returns.text == i18n.get(answer_text, new_category_name=new_category_name)
                assert handler_returns.reply_markup == markup

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, CategoryCD(operation=CategoryOperation.DEL, category_id=1, category_name='1').pack(),
             'rm_category_text',  does_not_raise()),
            (MAIN_USER_ID, CategoryCD(operation=CategoryOperation.DEL, category_id=1, category_name='1').pack(),
             'categories_is_fake_text', does_not_raise()),
            (MAIN_USER_ID, CategoryCD(operation=CategoryOperation.READ, category_id=1, category_name='1').pack(),
             'categories_is_fake_text', pytest.raises(AssertionError)),
            (99999, CategoryCD(operation=CategoryOperation.DEL, category_id=0, category_name='0').pack(),
             'categories_is_fake_text', does_not_raise()),
        ]
    )
    async def test_del_category(
            self, user_id: int, answer_text: str, expectation: does_not_raise,
            execute_callback_query_handler, buttons: AppButtons,
            i18n, redis_cli, data,
    ):
        await redis_hmset_create_tracker(
                user_id=MAIN_USER_ID, tracker_id='1', action_id=1, action_name='some_name',
                category_id=1, category_name='0', redis_client=redis_cli)

        handler_returns = await execute_callback_query_handler(user_id, data=data)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text)
            assert not await is_redis_hexists_tracker(user_id, redis_client=redis_cli)
            assert handler_returns.reply_markup == await menu_inline_kb(await buttons.category_menu_buttons(), i18n)

