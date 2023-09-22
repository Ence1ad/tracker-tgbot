from contextlib import nullcontext as does_not_raise

import pytest
from aiogram.methods import SendMessage, EditMessageText, AnswerCallbackQuery
from fluentogram import TranslatorRunner
from pytest_asyncio.plugin import SimpleFixtureFunction, FactoryFixtureFunction
from redis.asyncio import Redis
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_language_commands import redis_hget_lang
from cache.redis_schedule_command import is_redis_sismember_user
from config import settings
from db import UserModel
from tgbot.handlers.common_handles.settings_handler import _get_right_markup
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb, menu_inline_kb
from tgbot.utils.answer_text import started_tracker_text
from tgbot.utils.bot_commands import CommandName
from .utils import USER_ID
from tgbot.utils.jinja_engine import render_template

@pytest.mark.asyncio
class TestCommonHandlers:
    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (USER_ID, "/" + CommandName.START.name, 'new_user_text', does_not_raise()),  # add the user to the db and the redis set
            (USER_ID, "/" + CommandName.START.name,  None, does_not_raise()),  # checking the answer text when user tracker was launched
            (12345, "/" + CommandName.START.name,  'new_user_text', does_not_raise()),  # add the user to the db and the redis set
            (12345, "/" + CommandName.START.name, 'user_in_db_text', does_not_raise()),  # check the user in the db and in the redis set
            (12345, "/" + CommandName.START.name, 'user_in_db_text', does_not_raise()),
            (12345, "/" + CommandName.START.name, 'new_user_text', pytest.raises(AssertionError)),
            (USER_ID, "/" + CommandName.HELP.name, 'new_user_text', pytest.raises(AssertionError)),
            (USER_ID, None, 'new_user_text', pytest.raises(AssertionError)),
            (USER_ID, "/" + CommandName.START.name, '', pytest.raises(AssertionError)),
            (USER_ID, CommandName.START.name, None, pytest.raises(AssertionError)),
        ]
    )
    @pytest.mark.asyncio
    async def test_command_start_handler(
            self, get_tracker: SimpleFixtureFunction, user_id: int, answer_text: str, command: str,
            expectation: does_not_raise, redis_cli: Redis, buttons: AppButtons, i18n: TranslatorRunner,
            execute_message_handler: FactoryFixtureFunction, bot_db_session: async_sessionmaker[AsyncSession],
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, command=command)

        if answer_text is None:
            result_text = await started_tracker_text(user_id=user_id, redis_client=redis_cli, i18n=i18n,
                                                     title='started_tracker_title')
        else:
            result_text = i18n.get(answer_text)
        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.text == result_text
            assert handler_returns.reply_markup == await start_menu_inline_kb(await buttons.main_menu_buttons(), i18n)
            user_in_cache = await is_redis_sismember_user(user_id, redis_client=redis_cli)
            assert user_in_cache is True
            async with bot_db_session() as session:
                async with session.begin():
                    stmt = sa.select(UserModel.user_id).where(UserModel.user_id == user_id)
                    user_in_db = await session.execute(stmt)
            assert user_in_db.scalar_one_or_none() == user_id

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (USER_ID, AppButtons.general_data.EXIT_BTN.name, None, does_not_raise()),
            (USER_ID, AppButtons.general_data.EXIT_BTN.name, 'options_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.general_data.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_data.EXIT_BTN.name, 'options_text', does_not_raise()),
            (12345, None, 'options_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.general_data.EXIT_BTN.name, None, does_not_raise()),
            (USER_ID, AppButtons.general_data.EXIT_BTN.name, 'options_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.general_data.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_data.EXIT_BTN.name, 'options_text', does_not_raise()),
            (12345, None, 'options_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_exit_menu_handler(
            self, get_tracker: SimpleFixtureFunction, execute_callback_query_handler: FactoryFixtureFunction,
            redis_cli: Redis, user_id: int, answer_text: str, data: str, expectation: does_not_raise,
            buttons: AppButtons, i18n: TranslatorRunner
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
            # user_in_cache = await is_redis_sismember_user(user_id, redis_client=redis_cli)
            # assert user_in_cache is True

    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (USER_ID, "/" + CommandName.CANCEL.name, 'canceling_text', does_not_raise()),
            (44444, "/" + CommandName.CANCEL.name, 'canceling_text', does_not_raise()),
            (USER_ID, '', 'options_text', pytest.raises(AssertionError)),
            (USER_ID, "/" + CommandName.CANCEL.name, 'pass not correct text', pytest.raises(AssertionError)),
        ]
    )
    async def test_command_cancel_handler(
            self, execute_message_handler: FactoryFixtureFunction, user_id: int, command: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, command=command)
        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.text == i18n.get(answer_text)
            assert handler_returns.reply_markup is None

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (USER_ID, AppButtons.general_data.CANCEL_BTN.name, 'exit_text', does_not_raise()),
            (44444, AppButtons.general_data.CANCEL_BTN.name, 'exit_text', does_not_raise()),
            (USER_ID, None, 'options_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.general_data.CANCEL_BTN.name, 'pass not correct text', pytest.raises(AssertionError)),
            (USER_ID, 'pass not correct data', 'exit_text', pytest.raises(AssertionError)),
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
            (USER_ID, '/' + CommandName.HELP.name, does_not_raise()),
            (44444, '/' + CommandName.HELP.name, does_not_raise()),
            # (44444, '/' + CommandName.HELP.name, '', pytest.raises(AssertionError)),
            (USER_ID, 'pass not correct command', pytest.raises(AssertionError)),
            # (USER_ID, '/' + CommandName.HELP.name, 'pass not correct text', pytest.raises(AssertionError)),
        ]
    )
    async def test_command_help_handler(
            self, execute_message_handler: FactoryFixtureFunction, user_id: int, command: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, command=command)
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
            (USER_ID, '/' + CommandName.SETTINGS.name, 'options_text', does_not_raise()),
            (44444, '/' + CommandName.SETTINGS.name, 'options_text', does_not_raise()),
            (44444, '/' + CommandName.SETTINGS.name, '', pytest.raises(AssertionError)),
            (USER_ID, 'pass not correct command', 'options_text', pytest.raises(AssertionError)),
            # (USER_ID, '/' + CommandName.HELP.name, 'pass not correct text', pytest.raises(AssertionError)),
        ]
    )
    async def test_command_settings_handler(
            self, execute_message_handler: FactoryFixtureFunction, user_id: int, command: str,
            expectation: does_not_raise, i18n: TranslatorRunner, answer_text: str,
            buttons: AppButtons
    ):
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, command=command)
        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.text == i18n.get(answer_text)
            assert handler_returns.reply_markup == await menu_inline_kb(buttons=await buttons.settings_menu(),
                                                                        i18n=i18n)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (USER_ID, AppButtons.settings_data.LANGUAGE.name, 'select_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.LANGUAGE.name, 'select_lang_text', does_not_raise()),
            (USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.settings_data.LANGUAGE.name, 'pass not correct text', pytest.raises(AssertionError)),
            (USER_ID, 'pass not correct data', 'select_lang_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_set_user_language(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, buttons: AppButtons, redis_cli: Redis
    ):
        handler_returns: EditMessageText = await execute_callback_query_handler(user_id=user_id, data=data)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == i18n.get(answer_text)
            local = await redis_hget_lang(user_id, redis_client=redis_cli)
            assert handler_returns.reply_markup == await _get_right_markup(buttons=buttons, i18n=i18n,
                                                                           redis_client=redis_cli, local=local)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (USER_ID, AppButtons.settings_data.RUSSIA.name, 'set_lang_text', does_not_raise()),
            (USER_ID, AppButtons.settings_data.X_RUSSIA.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.RUSSIA.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.X_RUSSIA.name, 'set_lang_text', does_not_raise()),
            (USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.settings_data.RUSSIA.name, 'pass not correct text', does_not_raise()),
            (USER_ID, 'pass not correct data', 'select_lang_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_set_ru_lang(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis
    ):
        handler_returns:  AnswerCallbackQuery = await execute_callback_query_handler(user_id=user_id, data=data)
        lang_code: str = await redis_hget_lang(user_id, redis_cli)
        with expectation:
            assert isinstance(handler_returns,  AnswerCallbackQuery)
            print(handler_returns.text)
            assert lang_code in handler_returns.text

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (USER_ID, AppButtons.settings_data.ENGLISH.name, 'set_lang_text', does_not_raise()),
            (USER_ID, AppButtons.settings_data.X_ENGLISH.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.ENGLISH.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_data.X_ENGLISH.name, 'set_lang_text', does_not_raise()),
            (USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (USER_ID, AppButtons.settings_data.LANGUAGE.name, 'pass not correct text', pytest.raises(AssertionError)),
            (USER_ID, 'pass not correct data', 'select_lang_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_set_en_lang(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis
    ):
        handler_returns:  AnswerCallbackQuery = await execute_callback_query_handler(user_id=user_id, data=data)
        lang_code: str = await redis_hget_lang(user_id, redis_cli)
        with expectation:
            assert isinstance(handler_returns,  AnswerCallbackQuery)
            assert lang_code in handler_returns.text
