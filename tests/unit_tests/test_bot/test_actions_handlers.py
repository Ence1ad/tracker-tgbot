from contextlib import nullcontext as does_not_raise
from datetime import datetime
from enum import Enum

import pytest
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.methods import EditMessageText, SendMessage
from aiogram.types import Message
from fluent_compiler.errors import FluentReferenceError
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache.redis_tracker_commands import is_redis_hexists_tracker, redis_hget_tracker_data, \
    redis_hgetall_started_tracker
from config import settings
from db.actions.actions_db_commands import select_category_actions
from db.categories.categories_commands import select_categories
from tests.unit_tests.mocked_bot import MockedBot

from tests.unit_tests.test_bot.utils import TEST_CHAT
from tests.unit_tests.utils import MAIN_USER_ID, SECOND_USER_ID
from tgbot.handlers.actions_handlers.read_actions import _actions_list
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import ActionOperation, CategoryCD, CategoryOperation, ActionCD
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.states import ActionState


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestActionsHandlers:
    USER_WITHOUT_ACTION = 12345

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, ActionState.WAIT_CATEGORY_DATA, CategoryOperation.READ, 'selected_category', does_not_raise()),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, CategoryOperation.READ, 'selected_category', does_not_raise()),
            (USER_WITHOUT_ACTION, ActionState.WAIT_CATEGORY_DATA, CategoryOperation.READ, 'empty_actions_text', does_not_raise()),
            (USER_WITHOUT_ACTION, ActionState.WAIT_CATEGORY_DATA, CategoryOperation.READ, 'selected_category', pytest.raises(FluentReferenceError)),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, CategoryOperation.READ, 'empty_actions_text', pytest.raises(AssertionError)),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, ActionOperation.READ, 'empty_actions_text', pytest.raises(AssertionError)),
            (SECOND_USER_ID, ActionState.GET_NAME, CategoryOperation.READ, 'empty_actions_text', pytest.raises(AssertionError)),

        ]
    )
    async def test_get_actions_options(
            self,  user_id: int, answer_text: str, expectation: does_not_raise, execute_callback_query_handler,
            i18n,  bot, buttons, db_session, state: FSMContext, operation: Enum, db_category_factory,
            dispatcher: Dispatcher
    ):
        # Create category if user don't have it
        await db_category_factory(user_id)

        categories_lst = await select_categories(user_id, db_session)
        category_id = categories_lst[0].category_id
        category_name = categories_lst[0].category_name
        data = CategoryCD(operation=operation, category_id=category_id, category_name=category_name)
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)

        await dispatcher.fsm.storage.set_data(key=key,
                                              data={'category_id': category_id, "category_name": category_name})
        actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        with expectation:
            handler_returns = await execute_callback_query_handler(user_id, data=data.pack(), state=state)
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
            if actions:
                actions_list_text = await _actions_list(actions)
                assert handler_returns.text == i18n.get(answer_text, category_name=category_name,
                                                        new_line='\n', actions_list_text=actions_list_text)
            else:
                assert handler_returns.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (USER_WITHOUT_ACTION, AppButtons.actions_data.USER_ACTIONS.name, 'empty_actions_text', does_not_raise()),
            (SECOND_USER_ID, AppButtons.actions_data.USER_ACTIONS.name, 'show_action_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.actions_data.USER_ACTIONS.name, 'show_action_text', does_not_raise()),
            (MAIN_USER_ID, AppButtons.actions_data.USER_ACTIONS.name, 'empty_actions_text',
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.actions_data.USER_ACTIONS.name, '', pytest.raises(AssertionError)),
            (SECOND_USER_ID, AppButtons.actions_data.USER_ACTIONS.name, 'empty_actions_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_display_actions(
            self, user_id: int, answer_text: str, data: str, expectation: does_not_raise, dispatcher: Dispatcher,
            execute_callback_query_handler, i18n: TranslatorRunner, bot,
            db_session: async_sessionmaker[AsyncSession], buttons: AppButtons,
    ):
        state: FSMContext = dispatcher.fsm.get_context(bot=bot, chat_id=TEST_CHAT.id, user_id=user_id)
        state_data = await state.get_data()
        category_id = state_data['category_id']
        category_name = state_data['category_name']
        actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)

        with expectation:
            handler_returns = await execute_callback_query_handler(user_id, data=data)
            if actions:
                assert isinstance(handler_returns, SendMessage)
                actions_list_text = await _actions_list(actions)
                assert handler_returns.text == i18n.get(answer_text, category_name=category_name,
                                                        new_line='\n', actions_list_text=actions_list_text)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
            else:
                assert isinstance(handler_returns, EditMessageText)
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.new_action(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, data, answer_text, expectation",
        [
            (MAIN_USER_ID, ActionState.WAIT_CATEGORY_DATA, AppButtons.actions_data.CREATE_ACTIONS.name, 'action_limit_text', does_not_raise()),
            (USER_WITHOUT_ACTION, ActionState.WAIT_CATEGORY_DATA, AppButtons.actions_data.CREATE_ACTIONS.name, 'new_action_text', does_not_raise()),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, AppButtons.actions_data.CREATE_ACTIONS.name, 'new_action_text', does_not_raise()),
            (MAIN_USER_ID, ActionState.WAIT_CATEGORY_DATA, AppButtons.actions_data.CREATE_ACTIONS.name, None, pytest.raises(AssertionError)),

        ]
    )
    async def test_prompt_new_action_handler(
            self, user_id: int, answer_text: str, data: str, expectation: does_not_raise,
            execute_callback_query_handler, create_actions_more_than_limit, bot, dispatcher: Dispatcher,
            i18n: TranslatorRunner, buttons: AppButtons, state: FSMContext
    ):
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        storage_state = await dispatcher.fsm.storage.get_state(key)

        handler_returns = await execute_callback_query_handler(user_id=user_id, data=data)
        with expectation:
            assert storage_state == ActionState.WAIT_CATEGORY_DATA

            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text, action_limit=settings.USER_ACTIONS_LIMIT)
            if answer_text == 'category_limit_text':
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, new_action_name, answer_text, expectation",
        [
            (SECOND_USER_ID, ActionState.GET_NAME, 'my_new_action', 'added_new_action_text', does_not_raise()),
            (SECOND_USER_ID, ActionState.GET_NAME, 'my_new_action', 'action_exists_text', does_not_raise()),
            (USER_WITHOUT_ACTION, ActionState.GET_NAME, None, 'new_valid_action_name', does_not_raise()),
            (SECOND_USER_ID, ActionState.GET_NAME, 'not_exist!', 'action_exists_text', pytest.raises(AssertionError)),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, 'best_action', 'added_new_action_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_create_action_handler(
            self, user_id: int, answer_text: str, new_action_name: str, expectation: does_not_raise,  buttons: AppButtons,
            execute_message_handler, i18n: TranslatorRunner, state: FSMContext,
    ):
        test_message = Message(message_id=12345, date=datetime.now(), chat=TEST_CHAT, text=new_action_name)

        with expectation:
            handler_returns = await execute_message_handler(user_id, text=test_message.text, state=state)
            assert isinstance(handler_returns, SendMessage)
            if not isinstance(new_action_name, str):
                assert handler_returns.text == i18n.get(answer_text, new_line='\n')
            elif answer_text == 'action_exists_text':
                assert handler_returns.text == i18n.get(answer_text, new_action_name=new_action_name)
            else:
                assert handler_returns.text == i18n.get(answer_text, new_action_valid_name=new_action_name)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, cb_operation, expectation",
        [
            (MAIN_USER_ID, AppButtons.actions_data.UPDATE_ACTIONS.name, 'select_action_text', ActionOperation.UPD, does_not_raise()),
            (MAIN_USER_ID, AppButtons.actions_data.DELETE_ACTIONS.name, 'select_action_text', ActionOperation.DEL, does_not_raise()),
            (USER_WITHOUT_ACTION, AppButtons.actions_data.UPDATE_ACTIONS.name, 'empty_actions_text', ActionOperation.UPD, does_not_raise()),
            (USER_WITHOUT_ACTION, AppButtons.actions_data.DELETE_ACTIONS.name, 'empty_actions_text', ActionOperation.DEL, does_not_raise()),
            (SECOND_USER_ID, AppButtons.actions_data.UPDATE_ACTIONS.name, 'empty_actions_text', ActionOperation.UPD, pytest.raises(AssertionError)),
        ]
    )
    async def test_get_actions(
            self, user_id: int, answer_text: str, data: str, expectation: does_not_raise,
            execute_callback_query_handler, buttons: AppButtons, i18n, cb_operation: Enum, db_session,
            dispatcher, bot,
    ):
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        state_data = await dispatcher.fsm.storage.get_data(key)
        category_id = state_data['category_id']
        actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)

        handler_returns = await execute_callback_query_handler(user_id, data)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            if actions:
                assert handler_returns.reply_markup == await callback_factories_kb(actions, cb_operation)
            else:
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
            assert handler_returns.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, ActionState.UPDATE_NAME, ActionOperation.UPD, 'new_action_text', does_not_raise()),
            (SECOND_USER_ID, ActionState.UPDATE_NAME, ActionOperation.UPD, 'new_action_text', does_not_raise()),
            (USER_WITHOUT_ACTION, ActionState.UPDATE_NAME, ActionOperation.UPD, 'new_action_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_prompt_new_action_name(
            self,  user_id: int, answer_text: str, expectation: does_not_raise, execute_callback_query_handler,
            i18n,  bot, buttons, db_session, state: FSMContext, operation: Enum, db_category_factory,
            dispatcher: Dispatcher
    ):
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        state_data = await dispatcher.fsm.storage.get_data(key)
        category_id = state_data['category_id']
        category_name = state_data['category_name']
        actions_lst = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        data = None
        if actions_lst:
            action_id = actions_lst[0].action_id
            action_name = actions_lst[0].action_name
            data = ActionCD(operation=operation, action_id=action_id, action_name=action_name)
            await dispatcher.fsm.storage.set_data(
                key=key, data={'category_id': category_id, "category_name": category_name, 'action_id': action_id,
                               "action_name": action_name})
        with expectation:
            assert actions_lst != []
            assert (await dispatcher.fsm.storage.get_data(key)).get('action_id') is not None
            handler_returns = await execute_callback_query_handler(user_id=user_id, data=data.pack(), state=state)
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, state, new_action_name, answer_text, expectation",
        [

            (SECOND_USER_ID, ActionState.UPDATE_NAME, 'upd_action_name', 'upd_action_text', does_not_raise()),
            (SECOND_USER_ID, ActionState.UPDATE_NAME, 'upd_action_name', 'action_exists_text', does_not_raise()),
            (MAIN_USER_ID, ActionState.UPDATE_NAME, 'best_act', 'upd_action_text', does_not_raise()),
            (MAIN_USER_ID, ActionState.UPDATE_NAME, None, 'valid_action_name', does_not_raise()),


        ]
    )
    async def test_upd_action_name(
            self, user_id: int, new_action_name: str, state: FSMContext, expectation: does_not_raise,
            execute_message_handler, i18n: TranslatorRunner, bot: MockedBot, answer_text: str, dispatcher,
            buttons: AppButtons, redis_cli, create_tracker_fixt
    ):
        print(await redis_hgetall_started_tracker(user_id, redis_client=redis_cli))
        # key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        # state_data = await dispatcher.fsm.storage.get_data(key)
        test_message = Message(message_id=123456, date=datetime.now(), chat=TEST_CHAT, text=new_action_name)

        with expectation:
            handler_returns = await execute_message_handler(user_id=user_id, text=test_message.text, state=state)
            print(await redis_hgetall_started_tracker(user_id, redis_client=redis_cli))
            assert isinstance(handler_returns, SendMessage)
            if not isinstance(new_action_name, str):
                assert handler_returns.text == i18n.get(answer_text, new_line='\n')
            elif answer_text == 'action_exists_text':
                assert handler_returns.text == i18n.get(answer_text, new_action_name=new_action_name)
            else:
                assert handler_returns.text == i18n.get(answer_text)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
                assert await redis_hget_tracker_data(user_id, redis_client=redis_cli, key='action_name')\
                            == str(new_action_name).encode(encoding='utf-8')

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, ActionState.WAIT_CATEGORY_DATA, ActionOperation.DEL, 'rm_action_text', does_not_raise()),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, ActionOperation.DEL, 'rm_action_text', does_not_raise()),
            (SECOND_USER_ID, ActionState.WAIT_CATEGORY_DATA, ActionOperation.DEL, 'action_not_exists_text', does_not_raise()),
            (MAIN_USER_ID, ActionState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER, 'rm_action_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_del_action(
            self, user_id: int, answer_text: str, expectation: does_not_raise, state,
            execute_callback_query_handler, buttons: AppButtons, dispatcher, bot,
            i18n, redis_cli, create_tracker_fixt_fact, operation, db_session
    ):
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        state_data = await dispatcher.fsm.storage.get_data(key)
        category_id = state_data['category_id']
        actions_lst = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        data = action_name = ''
        if actions_lst:
            action_id = actions_lst[0].action_id
            action_name = actions_lst[0].action_name
            data = ActionCD(operation=operation, action_id=action_id, action_name=action_name)
            if user_id == SECOND_USER_ID:
                data = ActionCD(operation=operation, action_id=13, action_name='my_new_action')

        handler_returns = await execute_callback_query_handler(user_id, data=data.pack(), state=state)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            if not actions_lst:
                assert handler_returns.text == i18n.get(answer_text)
            else:
                assert handler_returns.text == i18n.get(answer_text, action_name=action_name)
                assert handler_returns.reply_markup == await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
                assert await is_redis_hexists_tracker(user_id, redis_client=redis_cli) is False
