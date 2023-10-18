from contextlib import nullcontext as does_not_raise
from datetime import datetime
from typing import Any

import pytest
import pytest_asyncio
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.methods import SendMessage, EditMessageText
from aiogram.types import Message, Chat
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.trackers_redis_manager import redis_hmset_create_tracker, \
    is_redis_hexists_tracker
from config import settings
from db.operations.actions_operations import create_actions
from db.operations.categories_operations import select_categories, create_category, \
    delete_category, \
    select_categories_with_actions
from tests.integration.mocked_bot import MockedBot
from tests.utils import MAIN_USER_ID, OTHER_USER_ID, CATEGORY_NAME, ACTION_NAME
from tgbot.handlers.categories_handlers.read_categories import _categories_list, \
    _get_operation
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryOperation, CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.states import CategoryState


@pytest.mark.usefixtures('create_categories_more_than_limit')
@pytest.mark.asyncio
class TestCategoriesHandlers:
    @pytest_asyncio.fixture(scope="class")
    async def create_categories_more_than_limit(
            self, db_user_factory, db_session_fixture: AsyncSession
    ) -> None:
        user_id = await db_user_factory(MAIN_USER_ID)
        for name in range(settings.USER_CATEGORIES_LIMIT):
            await create_category(user_id=user_id, category_name=str(name),
                                  db_session=db_session_fixture)
        try:
            yield
        finally:
            for cat_id in range(settings.USER_CATEGORIES_LIMIT):
                await delete_category(user_id=user_id, category_id=cat_id + 1,
                                      db_session=db_session_fixture)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.categories_btn_source.CREATE_CATEGORIES.name,
             'category_limit_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.categories_btn_source.CREATE_CATEGORIES.name,
             'new_category_text', pytest.raises(AssertionError)),
            (OTHER_USER_ID, AppButtons.categories_btn_source.CREATE_CATEGORIES.name,
             'new_category_text', does_not_raise()),
            (54321, AppButtons.categories_btn_source.CREATE_CATEGORIES.name, '',
             pytest.raises(AssertionError)),
            (12345, None, 'new_category_text', pytest.raises(AssertionError)),
            (100001, AppButtons.categories_btn_source.DELETE_CATEGORIES.name,
             'new_category_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_prompt_new_category_handler(
            self, user_id: int, answer_text: str, data: str,
            expectation: Any, execute_callback_query_handler, db_user_factory,
            i18n: TranslatorRunner, buttons: AppButtons
    ) -> None:
        await db_user_factory(user_id)  # Add all user to the db
        handler_returns = await execute_callback_query_handler(user_id=user_id,
                                                               data=data)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(
                answer_text, category_limit=settings.USER_CATEGORIES_LIMIT
            )
            if answer_text == 'category_limit_text':
                assert handler_returns.reply_markup == await menu_inline_kb(
                    await buttons.categories_btn_source.category_menu_buttons(), i18n
                )

    @pytest.mark.parametrize(
        "user_id, state, new_category_name, answer_text, expectation",
        [
            (100001, CategoryState.GET_NAME, 'cat_name_from_user',
             'added_new_category_text', does_not_raise()),
            (100001, CategoryState.GET_NAME, 'cat_name_from_user',
             'category_exists_text', does_not_raise()),
            (OTHER_USER_ID, CategoryState.GET_NAME, CATEGORY_NAME,
             'added_new_category_text', does_not_raise()),
            (OTHER_USER_ID, CategoryState.GET_NAME, CATEGORY_NAME,
             'category_exists_text', does_not_raise()),
            (100001, CategoryState.GET_NAME, 'cat_name_from_user',
             'added_new_category_text',
             pytest.raises(AssertionError)),
            (100001, CategoryState.GET_NAME, 'cat_name_from_user', '',
             pytest.raises(AssertionError)),
            (100001, CategoryState.GET_NAME, '', 'added_new_category_text',
             pytest.raises(AssertionError)),
            (100001, CategoryState.GET_NAME, None, 'added_new_category_text',
             pytest.raises(AssertionError)),
            (100001, None, 'cat_name_from_user', 'added_new_category_text',
             pytest.raises(AssertionError)),
        ]
    )
    async def test_create_category_handler(
            self, user_id: int, new_category_name: str, state: FSMContext,
            expectation: Any, execute_message_handler, i18n: TranslatorRunner,
            bot, answer_text: str, chat_fixt_fact,
            db_session_fixture: AsyncSession, buttons: AppButtons,
            redis_storage: RedisStorage
    ) -> None:
        chat: Chat = await chat_fixt_fact(user_id)
        test_message = Message(message_id=1234, date=datetime.now(), chat=chat,
                               text=new_category_name)
        handler_returns = await execute_message_handler(user_id=user_id,
                                                        text=test_message.text,
                                                        state=state)
        with expectation:
            state_data = await redis_storage.get_data(
                key=StorageKey(bot_id=bot.id, chat_id=chat.id, user_id=user_id))

            if state_data == {}:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(
                    await buttons.categories_btn_source.category_menu_buttons(), i18n
                )
                assert new_category_name == \
                       (await select_categories(user_id, db_session_fixture))[
                           0].category_name
                assert state_data == {}
            else:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == i18n.get(
                    answer_text, new_category_name=new_category_name, new_line='\n'
                )
                assert state_data['category_name'] == new_category_name

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (12345, AppButtons.general_btn_source.CATEGORIES_BTN.name,
             'empty_categories_text', does_not_raise()),
            (12345, AppButtons.general_btn_source.CATEGORIES_BTN.name,
             'show_categories_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.CATEGORIES_BTN.name,
             'show_categories_text', does_not_raise()),
            (OTHER_USER_ID, AppButtons.general_btn_source.CATEGORIES_BTN.name,
             'show_categories_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.CATEGORIES_BTN.name,
             'empty_categories_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.CATEGORIES_BTN.name, '',
             pytest.raises(AssertionError)),
            (12345, AppButtons.general_btn_source.ACTIONS_BTN.name,
             'empty_categories_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_display_categories(
            self, user_id: int, answer_text: str, data: str,
            expectation: Any, execute_callback_query_handler,
            i18n: TranslatorRunner, db_session_fixture: AsyncSession,
            buttons: AppButtons
    ) -> None:
        handler_returns = await execute_callback_query_handler(user_id, data)
        categories = await select_categories(user_id, db_session_fixture)
        with expectation:

            columns_list_text = await _categories_list(categories)
            if categories:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == f"{i18n.get(answer_text)}\n" \
                                               f"\r{columns_list_text}"
                assert handler_returns.reply_markup == await menu_inline_kb(
                    await buttons.categories_btn_source.category_menu_buttons(), i18n
                )
            else:
                assert isinstance(handler_returns, SendMessage)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(
                    await buttons.categories_btn_source.new_category(), i18n
                )

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.categories_btn_source.DELETE_CATEGORIES.name,
             'select_category_text', does_not_raise()),
            (OTHER_USER_ID, AppButtons.categories_btn_source.UPDATE_CATEGORIES.name,
             'select_category_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.ACTIONS_BTN.name,
             'select_category_text', does_not_raise()),
            (54321, AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'empty_categories_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'select_category_text', does_not_raise()),
            (100001, AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'empty_category_actions_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.categories_btn_source.CREATE_CATEGORIES.name,
             'select_category_text',
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.categories_btn_source.UPDATE_CATEGORIES.name,
             'empty_categories_text',
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.ACTIONS_BTN.name,
             'empty_categories_text',
             pytest.raises(AssertionError)),
        ]
    )
    async def test_categories_main_menu_handler(
            self, user_id: int, answer_text: str, data: str,
            expectation: Any, execute_callback_query_handler, buttons: AppButtons,
            i18n: TranslatorRunner, db_session_fixture,
    ) -> None:

        operation = await _get_operation(data, buttons)
        categories = await select_categories(user_id, db_session_fixture)
        if (user_id == MAIN_USER_ID) and \
                (data == AppButtons.trackers_btn_source.START_TRACKER_BTN.name):
            await create_actions(
                user_id=user_id, action_name=ACTION_NAME, category_id=1,
                db_session=db_session_fixture
            )
        handler_returns = await execute_callback_query_handler(user_id, data)
        with expectation:
            if categories and operation != CategoryOperation.READ_TRACKER:
                assert isinstance(handler_returns, EditMessageText)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await callback_factories_kb(
                    categories, operation)
            elif categories and operation == CategoryOperation.READ_TRACKER:
                categories_with_actions = await select_categories_with_actions(
                    user_id, db_session_fixture
                )
                if not categories_with_actions:
                    assert handler_returns.text == i18n.get(answer_text)
                    assert handler_returns.reply_markup == await menu_inline_kb(
                        await buttons.general_btn_source.main_menu_buttons(), i18n)
                else:
                    assert handler_returns.text == i18n.get(answer_text)
                    assert handler_returns.reply_markup == await callback_factories_kb(
                        categories_with_actions,
                        operation)
            else:
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(
                    await buttons.categories_btn_source.new_category(), i18n
                )

    @pytest.mark.parametrize(
        "user_id, operation, answer_text, expectation",
        [
            (OTHER_USER_ID, CategoryOperation.UPD, 'new_category_text',
             does_not_raise()),
            (100001, CategoryOperation.UPD, 'new_category_text',
             does_not_raise()),
            (OTHER_USER_ID, CategoryOperation.UPD, 'categories_is_fake_text',
             pytest.raises(AssertionError)),
            (OTHER_USER_ID, CategoryOperation.READ, 'new_category_text',
             pytest.raises(AssertionError)),
            (12345, CategoryOperation.UPD, 'new_category_text',
             pytest.raises(AssertionError)),
        ]
    )
    async def test_prompt_category_name(
            self, user_id: int, answer_text: str, expectation: Any,
            execute_callback_query_handler, bot: MockedBot,
            db_session_fixture: AsyncSession,
            i18n: TranslatorRunner, operation, dispatcher, chat_fixt_fact
    ) -> None:
        chat: Chat = await chat_fixt_fact(user_id)
        state: FSMContext = dispatcher.fsm.get_context(bot=bot, chat_id=chat.id,
                                                       user_id=user_id)
        state_data = await state.get_data()
        category = await select_categories(user_id, db_session=db_session_fixture)
        category_name = handler_returns = None
        if category:
            category_id = category[0][0]
            category_name = category[0][1]
            data = CategoryCD(operation=operation, category_id=category_id,
                              category_name=category_name)
            handler_returns = await execute_callback_query_handler(user_id,
                                                                   data=data.pack())
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text)
            assert state_data['category_name'] == category_name

    @pytest.mark.parametrize(
        "user_id, state, old_category_name, new_category_name, answer_text,"
        " expectation",
        [
            (OTHER_USER_ID, CategoryState.WAIT_CATEGORY_DATA, CATEGORY_NAME,
             'new_cat_name_from_user', 'upd_category_text', does_not_raise()),
            (OTHER_USER_ID, CategoryState.WAIT_CATEGORY_DATA, CATEGORY_NAME,
             CATEGORY_NAME, 'category_exists_text', does_not_raise()),
            (OTHER_USER_ID, CategoryState.WAIT_CATEGORY_DATA, CATEGORY_NAME,
             'category_exists_text', 'upd_category_text', does_not_raise()),

            (100001, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user',
             'name_from_user', 'upd_category_text', does_not_raise()),
            (OTHER_USER_ID, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user',
             None, 'valid_category_name_text', pytest.raises(AssertionError)),
            (100001, CategoryState.WAIT_CATEGORY_DATA, None, 'new_cat_name_from_user',
             'valid_data_text', does_not_raise()),
            (100001, CategoryState.GET_NAME, None, 'new_cat_name_from_user',
             'valid_data_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, CategoryState.WAIT_CATEGORY_DATA, 'cat_name_from_user',
             'new_cat_name_from_user', 'upd_category_text',
             pytest.raises(AssertionError))
        ]
    )
    async def test_upd_category_name(
            self, user_id: int, new_category_name: str, state: FSMContext,
            expectation: Any, execute_message_handler, i18n: TranslatorRunner,
            bot: MockedBot, answer_text: str, buttons: AppButtons,
            redis_storage: RedisStorage, old_category_name: str, chat_fixt_fact
    ) -> None:
        chat: Chat = await chat_fixt_fact(user_id)
        key = StorageKey(bot_id=bot.id, chat_id=chat.id, user_id=user_id)
        await redis_storage.set_data(key, data={"category_id": 1,
                                                'old_category_name': old_category_name})
        test_message = Message(message_id=12345, date=datetime.now(), chat=chat,
                               text=new_category_name)
        handler_returns = await execute_message_handler(user_id=user_id,
                                                        text=test_message.text,
                                                        state=state)
        with expectation:
            state_data = await redis_storage.get_data(key=key)

            assert isinstance(handler_returns, SendMessage)
            markup = await menu_inline_kb(
                await buttons.categories_btn_source.category_menu_buttons(), i18n)
            assert state_data == {}
            if not isinstance(new_category_name, str):
                assert handler_returns.text == i18n.get(answer_text, new_line='\n')
                assert handler_returns.reply_markup == markup
            elif answer_text == 'category_exists_text':
                assert handler_returns.text == i18n.get(
                    answer_text, new_category_name=new_category_name, new_line='\n')
                assert handler_returns.reply_markup == markup
            elif not old_category_name:
                assert handler_returns.text == i18n.get(answer_text)
            else:
                assert handler_returns.text == i18n.get(
                    answer_text, new_category_name=new_category_name
                )
                assert handler_returns.reply_markup == markup

    @pytest.mark.parametrize(
        "user_id, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, CategoryOperation.DEL, 'rm_category_text', does_not_raise()),
            (OTHER_USER_ID, CategoryOperation.DEL, 'rm_category_text',
             does_not_raise()),
            (100001, CategoryOperation.DEL, 'rm_category_text', does_not_raise()),
            (OTHER_USER_ID, CategoryOperation.DEL, 'categories_is_fake_text',
             does_not_raise()),
        ]
    )
    async def test_delete_category_handler(
            self, user_id: int, answer_text: str, expectation: Any,
            execute_callback_query_handler, buttons: AppButtons, db_session_fixture,
            i18n: TranslatorRunner, redis_cli: Redis, operation,
    ) -> None:
        await redis_hmset_create_tracker(
            user_id=MAIN_USER_ID, tracker_id='1', action_id=1, action_name='some_name',
            category_id=1, category_name='0', redis_client=redis_cli)
        category = await select_categories(user_id, db_session=db_session_fixture)
        category_id = category_name = None
        if category:
            category_id = category[0][0]
            category_name = category[0][1]
        if user_id == OTHER_USER_ID:
            category_id = 12
            category_name = CATEGORY_NAME

        data = CategoryCD(operation=operation, category_id=category_id,
                          category_name=category_name)

        handler_returns = await execute_callback_query_handler(user_id,
                                                               data=data.pack())
        with expectation:
            if not category:
                assert handler_returns.text == i18n.get(answer_text)
            else:
                assert isinstance(handler_returns, EditMessageText)
                assert handler_returns.text == i18n.get(answer_text)
                assert not await is_redis_hexists_tracker(user_id,
                                                          redis_client=redis_cli)
                assert handler_returns.reply_markup == await menu_inline_kb(
                    await buttons.categories_btn_source.category_menu_buttons(), i18n
                )
