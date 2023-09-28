from contextlib import nullcontext as does_not_raise

import pytest
from aiogram.methods import SendMessage, EditMessageText, AnswerCallbackQuery
from fluentogram import TranslatorRunner
from pytest_asyncio.plugin import FactoryFixtureFunction
from redis.asyncio import Redis
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_language_commands import redis_hget_lang
from cache.redis_schedule_command import is_redis_sismember_user, redis_sadd_user_id
from cache.redis_tracker_commands import is_redis_hexists_tracker
from config import settings
from db import UserModel
from tgbot.handlers.common_handles.settings_handler import _get_right_markup, _get_language
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb, menu_inline_kb
from tgbot.utils.answer_text import started_tracker_text
from tgbot.utils.bot_commands import CommandName
from ..utils import MAIN_USER_ID
from tgbot.utils.jinja_engine import render_template


@pytest.mark.asyncio
class TestCommonHandlers:

    NEW_USER = 9999999999
    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (NEW_USER, "/" + CommandName.START.name, 'new_user_text', does_not_raise()),  # add the user to the db and the redis set
            (NEW_USER, "/" + CommandName.START.name, 'user_in_db_text', does_not_raise()),  # user all ready in db
            (MAIN_USER_ID, "/" + CommandName.START.name, 'new_user_text', does_not_raise()),  # user all ready in db
            (MAIN_USER_ID, "/" + CommandName.START.name,  None, does_not_raise()),  # checking the answer text when user tracker was launched
            (MAIN_USER_ID, "/" + CommandName.HELP.name, 'new_user_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, None, 'new_user_text', pytest.raises(AssertionError)),
            (NEW_USER, "/" + CommandName.START.name, '', pytest.raises(AssertionError)),
        ]
    )
    @pytest.mark.asyncio
    async def test_command_start_handler(
            self, create_tracker_fixt_fact, user_id: int, answer_text: str, command: str,
            expectation: does_not_raise, redis_cli: Redis, buttons: AppButtons, i18n: TranslatorRunner,
            execute_message_handler, db_session: AsyncSession,
    ):

        if (user_id == MAIN_USER_ID) and (answer_text is None):
            await create_tracker_fixt_fact(user_id,  category_id=1, category_name='new_cat', action_id='1', action_name='new_act',
                                           tracker_id='1')
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, text=command)

        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.reply_markup == await start_menu_inline_kb(await buttons.main_menu_buttons(), i18n)
            if await is_redis_hexists_tracker(user_id, redis_cli):
                assert handler_returns.text[:20] == (await started_tracker_text(user_id=user_id, redis_client=redis_cli, i18n=i18n,
                                                                          title='started_tracker_title'))[:20]
            elif await is_redis_sismember_user(user_id, redis_client=redis_cli):
                assert handler_returns.text == i18n.get(answer_text)
                print(handler_returns.text)
            else:
                assert handler_returns.text == i18n.get(answer_text)
                async with db_session as db_session:
                    async with db_session.begin():
                        stmt = sa.select(UserModel.user_id).where(UserModel.user_id == user_id)
                        user_in_db = await db_session.execute(stmt)
                assert user_in_db.scalar_one_or_none() == user_id

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.general_data.EXIT_BTN.name, None, does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_data.EXIT_BTN.name, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_data.EXIT_BTN.name, 'options_text', does_not_raise()),
            (12345, None, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.EXIT_BTN.name, None, does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_data.EXIT_BTN.name, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_data.EXIT_BTN.name, 'options_text', does_not_raise()),
            (12345, None, 'options_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_exit_menu_handler(
            self, execute_callback_query_handler, buttons: AppButtons, i18n: TranslatorRunner,
            redis_cli: Redis, user_id: int, answer_text: str, data: str, expectation: does_not_raise,

    ):
        handler_returns: EditMessageText = await execute_callback_query_handler(user_id, data)
        if answer_text is None:
            result_text = await started_tracker_text(user_id=user_id, redis_client=redis_cli, i18n=i18n,
                                                     title='started_tracker_title')
        else:
            result_text = i18n.get(answer_text)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == result_text
            assert handler_returns.reply_markup == await start_menu_inline_kb(await buttons.main_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (MAIN_USER_ID, "/" + CommandName.CANCEL.name, 'canceling_text', does_not_raise()),
            (44444, "/" + CommandName.CANCEL.name, 'canceling_text', does_not_raise()),
            (MAIN_USER_ID, '', 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, "/" + CommandName.CANCEL.name, 'pass not correct text', pytest.raises(AssertionError)),
        ]
    )
    async def test_command_cancel_handler(
            self, execute_message_handler: FactoryFixtureFunction, user_id: int, command: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, text=command)
        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.text == i18n.get(answer_text)
            assert handler_returns.reply_markup is None

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.general_data.CANCEL_BTN.name, 'exit_text', does_not_raise()),
            (44444, AppButtons.general_data.CANCEL_BTN.name, 'exit_text', does_not_raise()),
            (MAIN_USER_ID, None, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_data.CANCEL_BTN.name, 'pass not correct text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, 'pass not correct data', 'exit_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_button_cancel_handler(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner
    ):
        handler_returns: AnswerCallbackQuery = await execute_callback_query_handler(user_id=user_id, data=data)
        with expectation:
            assert isinstance(handler_returns, AnswerCallbackQuery)
            assert handler_returns.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, command, expectation",
        [
            (MAIN_USER_ID, '/' + CommandName.HELP.name, does_not_raise()),
            (44444, '/' + CommandName.HELP.name, does_not_raise()),
            (MAIN_USER_ID, 'pass not correct command', pytest.raises(AssertionError)),
        ]
    )
    async def test_command_help_handler(
            self, execute_message_handler, user_id: int, command: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, text=command)
        with expectation:
            local = await redis_hget_lang(user_id=user_id, redis_client=redis_cli)
            if local == settings.RU_LANG_CODE:
                answer_text = render_template('ru_help_handler.html')
            else:
                answer_text = render_template('en_help_handler.html')
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.text == answer_text
            assert handler_returns.reply_markup is None

    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (MAIN_USER_ID, '/' + CommandName.SETTINGS.name, 'options_text', does_not_raise()),
            (44444, '/' + CommandName.SETTINGS.name, 'options_text', does_not_raise()),
            (44444, '/' + CommandName.SETTINGS.name, '', pytest.raises(AssertionError)),
            (MAIN_USER_ID, 'pass not correct command', 'options_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_command_settings_handler(
            self, execute_message_handler, user_id: int, command: str,
            expectation: does_not_raise, i18n: TranslatorRunner, answer_text: str,
            buttons: AppButtons
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, text=command)
        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.text == i18n.get(answer_text)
            assert handler_returns.reply_markup == await menu_inline_kb(buttons=await buttons.settings_menu(),
                                                                        i18n=i18n)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.settings_data.LANGUAGE.name, 'select_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.LANGUAGE.name, 'select_lang_text', does_not_raise()),
            (MAIN_USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.settings_data.LANGUAGE.name, 'pass not correct text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, 'pass not correct data', 'select_lang_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_language_settings(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, buttons: AppButtons, redis_cli: Redis
    ):
        handler_returns: EditMessageText = await execute_callback_query_handler(user_id=user_id, data=data)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text)
            local = await redis_hget_lang(user_id, redis_client=redis_cli)
            assert handler_returns.reply_markup == await _get_right_markup(buttons=buttons, i18n=i18n,
                                                                           local=local)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.settings_data.X_RUSSIA.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.RUSSIA.name, 'set_lang_text', does_not_raise()),
            (MAIN_USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.settings_data.ENGLISH.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.X_ENGLISH.name, 'set_lang_text', does_not_raise()),
            (MAIN_USER_ID, 'pass not correct data', 'select_lang_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.settings_data.LANGUAGE.name, 'pass not correct text', pytest.raises(AssertionError)),
        ]
    )
    async def test_set_user_lang(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis, buttons: AppButtons,
            lang_bot_settings
    ):
        lang_code_before: str = await redis_cli.hget(name='lang', key=str(user_id))
        print('get_code_before:', lang_code_before)
        # choice_lang_code: str = await _get_language(call_data=data, buttons=buttons)
        handler_returns:  AnswerCallbackQuery = await execute_callback_query_handler(user_id=user_id, data=data)
        lang_code_after: str = await redis_cli.hget(name='lang', key=str(user_id))
        print('get_code_after:', lang_code_before)
        with expectation:
            assert isinstance(handler_returns,  AnswerCallbackQuery)
            assert handler_returns.text is not None
            # assert choice_lang_code == get_code_after
            if data is None:
                assert lang_code_after == lang_bot_settings
            elif data in ('RUSSIAN', 'X_RUSSIAN'):
                assert lang_code_after == settings.EN_LANG_CODE
            elif data in ('ENGLISH', 'X_ENGLISH'):
                assert lang_code_after == settings.RU_LANG_CODE
