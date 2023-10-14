from contextlib import nullcontext as does_not_raise

import pytest
from aiogram.methods import SendMessage, EditMessageText, AnswerCallbackQuery
from fluentogram import TranslatorRunner
from pytest_asyncio.plugin import FactoryFixtureFunction
from redis.asyncio import Redis

from cache.language_redis_manager import redis_hget_lang, LANG_PREFIX
from cache.redis_utils import set_redis_name
from cache.trackers_redis_manager import is_redis_hexists_tracker
from config import settings
from tests.utils import MAIN_USER_ID
from tgbot.handlers.common_handles.settings_handler import _get_right_markup
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb, menu_inline_kb
from tgbot.template_engine.jinja_engine import render_template
from tgbot.utils.answer_text import started_tracker_text
from tgbot.utils.bot_commands import CommandName


@pytest.mark.asyncio
class TestCommonHandlers:
    NEW_USER = 9999999999

    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (NEW_USER, "/" + CommandName.START.name, 'user_in_db_text', does_not_raise()),  # user all ready in db
            (MAIN_USER_ID, "/" + CommandName.START.name, 'user_in_db_text', does_not_raise()),  # user all ready in db
            (MAIN_USER_ID, "/" + CommandName.START.name, None, does_not_raise()),
            # checking the answer text when user tracker was launched
            (MAIN_USER_ID, "/" + CommandName.HELP.name, 'new_user_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, None, 'new_user_text', pytest.raises(AssertionError)),
            (NEW_USER, "/" + CommandName.START.name, '', pytest.raises(AssertionError)),
        ]
    )
    @pytest.mark.asyncio
    async def test_command_start_handler(
            self, create_tracker_fixt_fact, user_id: int, answer_text: str, command: str,
            expectation: does_not_raise, redis_cli: Redis, buttons: AppButtons, i18n: TranslatorRunner,
            execute_message_handler,
    ):

        if (user_id == MAIN_USER_ID) and (answer_text is None):
            await create_tracker_fixt_fact(user_id, category_id=1, category_name='new_cat', action_id='1',
                                           action_name='new_act',
                                           tracker_id='1')
        handler_returns: SendMessage = await execute_message_handler(user_id=user_id, text=command)

        with expectation:
            assert isinstance(handler_returns, SendMessage)
            assert handler_returns.reply_markup == await start_menu_inline_kb(
                await buttons.general_btn_source.main_menu_buttons(), i18n)
            if await is_redis_hexists_tracker(user_id, redis_cli):
                assert handler_returns.text[:20] == (await started_tracker_text(user_id=user_id, redis_client=redis_cli,
                                                                                i18n=i18n,
                                                                                title='started_tracker_title'))[:20]
            else:
                assert handler_returns.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.general_btn_source.EXIT_BTN.name, None, does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.EXIT_BTN.name, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_btn_source.EXIT_BTN.name, 'options_text', does_not_raise()),
            (12345, None, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.EXIT_BTN.name, None, does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.EXIT_BTN.name, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_btn_source.EXIT_BTN.name, 'options_text', does_not_raise()),
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
            assert handler_returns.reply_markup == await start_menu_inline_kb(
                await buttons.general_btn_source.main_menu_buttons(), i18n)

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
            (MAIN_USER_ID, AppButtons.general_btn_source.CANCEL_BTN.name, 'exit_text', does_not_raise()),
            (44444, AppButtons.general_btn_source.CANCEL_BTN.name, 'exit_text', does_not_raise()),
            (MAIN_USER_ID, None, 'options_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.general_btn_source.CANCEL_BTN.name, 'pass not correct text',
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, 'pass not correct data', 'exit_text', pytest.raises(AssertionError)),
        ]
    )
    async def test_button_cancel_handler(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner
    ):
        handler_returns = await execute_callback_query_handler(user_id=user_id, data=data)
        with expectation:
            assert isinstance(handler_returns, (AnswerCallbackQuery, EditMessageText))
            assert handler_returns.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, text, expectation",
        [
            (MAIN_USER_ID, '/help', does_not_raise()),
            (MAIN_USER_ID, '/help_cat', does_not_raise()),
            (MAIN_USER_ID, '/help_act', does_not_raise()),
            (MAIN_USER_ID, '/help_tra', does_not_raise()),
            (MAIN_USER_ID, '/help_rep', does_not_raise()),
            (44444, '/help', does_not_raise()),
            (MAIN_USER_ID, '/help_unknown', does_not_raise()),
            (MAIN_USER_ID, '/help this is incorrect', does_not_raise()),
        ]
    )
    async def test_command_help_handler(
            self, execute_message_handler, user_id: int, text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis
    ):
        local = await redis_hget_lang(user_id=user_id, redis_client=redis_cli)

        if local == settings.RU_LANG_CODE:
            lang_code: dict[str:str] = {
                "main": 'ru_help_main.html',
                "cat": 'ru_help_categories.html',
                "act": 'ru_help_actions.html',
                "tra": 'ru_help_trackers.html',
                "rep": 'ru_help_reports.html'
            }
        else:
            lang_code = {
                "main": 'en_help_main.html',
                "cat": 'en_help_categories.html',
                "act": 'en_help_actions.html',
                "tra": 'en_help_trackers.html',
                "rep": 'en_help_reports.html'
            }

        words = text.split('_')

        # If there is only one word (i.e., just "/help" without specifying a command)
        if len(words) == 1:
            # Provide a general help message
            answer_text: str = render_template(lang_code.get("main"))
        elif len(words) == 2:
            command = words[1]
            html_doc = lang_code.get(command)
            if html_doc is not None:
                answer_text = render_template(html_doc)
            else:
                answer_text = i18n.get('help_unknown_command_text')

        else:
            answer_text = i18n.get('help_invalid_command_format_text')

        handler_returns = await execute_message_handler(user_id=user_id, text=text)
        with expectation:
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
            assert handler_returns.reply_markup == await menu_inline_kb(
                buttons=await buttons.settings_btn_source.settings_menu(),
                i18n=i18n)

    @pytest.mark.parametrize(
        "user_id, data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.settings_btn_source.LANGUAGE.name, 'select_lang_text', does_not_raise()),
            (44444, AppButtons.settings_btn_source.LANGUAGE.name, 'select_lang_text', does_not_raise()),
            (MAIN_USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.settings_btn_source.LANGUAGE.name, 'pass not correct text',
             pytest.raises(AssertionError)),
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
            (MAIN_USER_ID, AppButtons.settings_btn_source.X_RUSSIA.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_btn_source.RUSSIA.name, 'set_lang_text', does_not_raise()),
            (MAIN_USER_ID, None, 'select_lang_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.settings_btn_source.ENGLISH.name, 'set_lang_text', does_not_raise()),
            (44444, AppButtons.settings_btn_source.X_ENGLISH.name, 'set_lang_text', does_not_raise()),
            (MAIN_USER_ID, 'pass not correct data', 'select_lang_text', pytest.raises(AssertionError)),
            (MAIN_USER_ID, AppButtons.settings_btn_source.LANGUAGE.name, 'pass not correct text',
             pytest.raises(AssertionError)),
        ]
    )
    async def test_set_user_lang(
            self, execute_callback_query_handler: FactoryFixtureFunction, user_id: int, data: str, answer_text: str,
            expectation: does_not_raise, i18n: TranslatorRunner, redis_cli: Redis, buttons: AppButtons,
            lang_bot_settings
    ):
        handler_returns = await execute_callback_query_handler(user_id=user_id, data=data)
        name = set_redis_name(user_id, prefix=LANG_PREFIX)
        lang_code_after: bytes = await redis_cli.hget(name=name, key=str(user_id))
        with expectation:
            assert isinstance(handler_returns, (AnswerCallbackQuery, SendMessage))
            assert handler_returns.text is not None
            if data is None:
                assert lang_code_after.decode(encoding='utf-8') == lang_bot_settings
            elif data in ('RUSSIAN', 'X_RUSSIAN'):
                assert lang_code_after.decode(encoding='utf-8') == settings.RU_LANG_CODE
            elif data in ('ENGLISH', 'X_ENGLISH'):
                assert lang_code_after.decode(encoding='utf-8') == settings.EN_LANG_CODE
