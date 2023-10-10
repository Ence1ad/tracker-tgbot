import datetime
from contextlib import nullcontext as does_not_raise

import pytest
import sqlalchemy as sa
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.methods import SendMessage, EditMessageText, SendDocument
from redis.asyncio import Redis
from sqlalchemy import cast, DATE

from cache.redis_report_commands import set_redis_name
from cache.redis_tracker_commands import is_redis_hexists_tracker, redis_get_user_day_trackers, \
    redis_incr_user_day_trackers, redis_hget_tracker_data, TRACKER_CNT_PREFIX
from config import settings
from db import TrackerModel
from db.actions.actions_db_commands import select_category_actions
from db.categories.categories_commands import select_categories
from db.report.report_commands import select_weekly_trackers
from db.tracker.tracker_db_command import select_stopped_trackers, select_tracker_duration
from tests.functional_tests.test_bot.utils import TEST_CHAT
from tests.utils import MAIN_USER_ID, SECOND_USER_ID, USER_ID_WITH_TRACKER_LIMIT
from tgbot.handlers.categories_handlers.read_categories import _get_operation
from tgbot.handlers.tracker_handlers.delete_tracker import _get_right_tracker_markup
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation, ActionCD, TrackerOperation, TrackerCD
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.answer_text import started_tracker_text
from tgbot.utils.states import TrackerState


@pytest.mark.usefixtures('add_data_to_db', 'create_tracker_fixt')
@pytest.mark.asyncio
class TestActionsHandlers:
    USER_WITHOUT_TRACKER = SECOND_USER_ID
    USER_WITHOUT_CATEGORIES = 55555

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT, AppButtons.general_btn_source.TRACKERS_BTN.name, 'started_tracker_title',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.TRACKERS_BTN.name, 'options_text', does_not_raise()),
            (USER_WITHOUT_TRACKER, AppButtons.trackers_btn_source.DURATION_TRACKER_BTN.name, 'options_text',
             does_not_raise()),

        ]
    )
    async def test_trackers_main_menu_handler(
            self, user_id: str, expectation, button_data: str, execute_callback_query_handler, answer_text: str,
            redis_cli, i18n, buttons,
    ):

        is_tracker = await is_redis_hexists_tracker(user_id=user_id, redis_client=redis_cli)
        with expectation:
            started_tracker_txt = await started_tracker_text(user_id=int(user_id), redis_client=redis_cli, i18n=i18n,
                                                             title=answer_text)
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, SendMessage)
            if is_tracker:
                assert handler_result.text[:10] == started_tracker_txt[:10]
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
            else:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.trackers_btn_source.START_TRACKER_BTN.name, 'select_category_text',
             does_not_raise()),
            (USER_ID_WITH_TRACKER_LIMIT, AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'tracker_daily_limit_text', does_not_raise()),
            (USER_WITHOUT_TRACKER, AppButtons.trackers_btn_source.START_TRACKER_BTN.name, 'select_category_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.trackers_btn_source.START_TRACKER_BTN.name, 'empty_categories_text',
             does_not_raise()),
        ]
    )
    async def test_pass_tracker_checks(
            self, user_id: int, expectation, button_data: str, execute_callback_query_handler, answer_text: str,
            redis_cli, i18n, buttons, db_session, db_user_factory
    ):
        await db_user_factory(user_id)
        is_tracker = await is_redis_hexists_tracker(user_id=user_id, redis_client=redis_cli)
        if is_tracker and USER_ID_WITH_TRACKER_LIMIT:
            for _ in range(settings.USER_TRACKERS_DAILY_LIMIT):
                await redis_incr_user_day_trackers(user_id, redis_client=redis_cli)
        user_trackers_cnt = await redis_get_user_day_trackers(user_id, redis_cli)

        handler_result = await execute_callback_query_handler(user_id, data=button_data)
        with expectation:
            assert isinstance(handler_result, (EditMessageText, SendMessage))
            if user_trackers_cnt is None or (int(user_trackers_cnt) < settings.USER_TRACKERS_DAILY_LIMIT):
                if categories := await select_categories(user_id, db_session):
                    operation = await _get_operation(call_data=button_data, buttons=buttons)
                    assert handler_result.text == i18n.get(answer_text)
                    assert handler_result.reply_markup == await callback_factories_kb(categories, operation)
                else:
                    assert handler_result.text == i18n.get(answer_text)
                    assert handler_result.reply_markup == await menu_inline_kb(
                        await buttons.categories_btn_source.new_category(), i18n
                    )
            else:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER, 'select_category_4_tracker',
             does_not_raise()),
            (USER_ID_WITH_TRACKER_LIMIT, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER,
             'select_category_4_tracker', does_not_raise()),
            (USER_WITHOUT_TRACKER, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER,
             'select_category_4_tracker', does_not_raise()),
            (USER_WITHOUT_CATEGORIES, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER, 'valid_data_text',
             does_not_raise()),
        ]
    )
    async def test_take_action_4_tracker(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str,
            i18n, buttons, db_session, state: FSMContext, operation, db_category_factory
    ):
        if user_id == TestActionsHandlers.USER_WITHOUT_CATEGORIES:
            await db_category_factory(user_id)
        categories_lst = await select_categories(user_id, db_session)
        category_id = categories_lst[0].category_id
        category_name = categories_lst[0].category_name
        data = CategoryCD(operation=operation, category_id=category_id, category_name=category_name)

        actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        handler_result = await execute_callback_query_handler(user_id, data=data.pack(), state=state)
        with expectation:
            assert isinstance(handler_result, (EditMessageText, SendMessage))
            if actions:
                assert handler_result.text == i18n.get(answer_text, category_name=category_name, new_line='\n')
                assert handler_result.reply_markup == await callback_factories_kb(actions, operation)
            else:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.general_btn_source.main_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER, 'new_tracker_text',
             does_not_raise()),
            (USER_ID_WITH_TRACKER_LIMIT, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER,
             'not_enough_data_text', does_not_raise()),
            (SECOND_USER_ID, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER, 'new_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, TrackerState.WAIT_CATEGORY_DATA, ActionOperation.READ_TRACKER,
             'new_tracker_text', pytest.raises(AssertionError)),  # this user don't have an actions
        ]
    )
    async def test_create_tracker(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli: Redis,
            i18n, buttons, db_session, state: FSMContext, operation, dispatcher: Dispatcher, bot, scheduler
    ):
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        state_data = await dispatcher.fsm.storage.get_data(key)
        category_id = state_data.get('category_id')
        data = action_name = None
        actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        if actions:
            action_id = actions[0].action_id
            action_name = actions[0].action_name
            data = ActionCD(operation=operation, action_id=action_id, action_name=action_name)
        before_handler = await is_redis_hexists_tracker(user_id, redis_cli)

        with expectation:
            assert actions
            handler_result = await execute_callback_query_handler(user_id, data=data.pack(), state=state)
            assert isinstance(handler_result, EditMessageText)
            after_handler = await is_redis_hexists_tracker(user_id, redis_cli)
            if before_handler == after_handler:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)
            else:
                name = set_redis_name(user_id, prefix=TRACKER_CNT_PREFIX)
                assert await redis_cli.get(name)  # check the redis_expireat_midnight func was started
                assert await redis_incr_user_day_trackers(user_id, redis_cli)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
                assert handler_result.text == i18n.get(answer_text, action_name=action_name)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name, 'answer_stop_tracker_text',
             does_not_raise()),
            (SECOND_USER_ID, AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name, 'answer_stop_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name, 'not_launched_tracker_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_check_is_launched_tracker(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data,
    ):
        is_tracker = await is_redis_hexists_tracker(user_id, redis_cli)

        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, SendMessage)
            if is_tracker:
                started_tracker = await started_tracker_text(user_id=user_id, redis_client=redis_cli, i18n=i18n,
                                                             title='started_tracker_title')
                assert handler_result.text[:20] == (started_tracker + i18n.get(answer_text))[:20]
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.general_btn_source.yes_no_menu(), i18n)
            else:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.general_btn_source.NO_BTN.name, 'options_text',
             does_not_raise()),
            (SECOND_USER_ID, AppButtons.general_btn_source.NO_BTN.name, 'options_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.general_btn_source.NO_BTN.name, 'options_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_stop_tracker_no_handler(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data,
    ):
        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, EditMessageText)
            assert handler_result.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.general_btn_source.YES_BTN.name, 'stop_tracker_text',
             does_not_raise()),
            (SECOND_USER_ID, AppButtons.general_btn_source.YES_BTN.name, 'stop_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.general_btn_source.YES_BTN.name, 'not_launched_tracker_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_stop_tracker_yes_handler(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data, db_session
    ):

        tracker_id = await redis_hget_tracker_data(user_id, redis_cli, 'tracker_id')
        track_text = await started_tracker_text(user_id=user_id, redis_client=redis_cli, i18n=i18n,
                                                title=answer_text)
        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, EditMessageText)
            if tracker_id:
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)
                assert handler_result.text[:20] == track_text[:20]
                assert not await is_redis_hexists_tracker(user_id, redis_cli)
                assert await select_tracker_duration(user_id=user_id, tracker_id=int(tracker_id),
                                                     db_session=db_session) != 0
            else:
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
                assert handler_result.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT, AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name,
             'empty_stopped_tracker_text',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name, 'daily_tracker_text',
             does_not_raise()),
            (SECOND_USER_ID, AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name, 'daily_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name,
             'empty_stopped_tracker_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_take_traker_4_delete(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data, db_session
    ):

        stopped_trackers = await select_stopped_trackers(user_id, db_session)
        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, (EditMessageText, SendMessage))
            if stopped_trackers:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await callback_factories_kb(stopped_trackers,
                                                                                  enum_val=TrackerOperation.DEL)
            else:
                assert handler_result.text == i18n.get(answer_text)
                await _get_right_tracker_markup(user_id, redis_cli, buttons, i18n)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT, AppButtons.general_btn_source.REPORTS_BTN.name, 'options_text',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.REPORTS_BTN.name, 'options_text',
             does_not_raise()),
            (SECOND_USER_ID, AppButtons.general_btn_source.REPORTS_BTN.name, 'options_text',
             does_not_raise()),

        ]
    )
    async def test_main_menu_reports_handler(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data, db_session
    ):

        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, EditMessageText)
            assert handler_result.text == i18n.get(answer_text)
            assert handler_result.reply_markup == await menu_inline_kb(await buttons.reports_btn_source.report_menu(),
                                                                       i18n)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT, AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name, 'empty_trackers_text',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name, 'send_report_text',
             does_not_raise()),
            (SECOND_USER_ID, AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name, 'send_report_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name, 'empty_trackers_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_get_weekly_report(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data, db_session
    ):

        report = await select_weekly_trackers(user_id, db_session)
        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, (EditMessageText, SendDocument))
            if report and isinstance(handler_result, SendDocument):
                assert handler_result.document.filename == settings.WEEKLY_XLSX_FILE_NAME
                assert handler_result.caption == i18n.get(answer_text)
            elif not report and isinstance(handler_result, EditMessageText):
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.general_btn_source.main_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, TrackerOperation.DEL, 'delete_tracker_text', does_not_raise()),
            (MAIN_USER_ID, TrackerOperation.DEL, 'already_delete_tracker_text', does_not_raise()),
            (SECOND_USER_ID, TrackerOperation.DEL, 'delete_tracker_text', does_not_raise()),
            (SECOND_USER_ID, TrackerOperation.DEL, 'already_delete_tracker_text', does_not_raise()),
        ]
    )
    async def test_delete_tracker_handler(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli: Redis,
            i18n, buttons, db_session, operation, dispatcher: Dispatcher, bot,
    ):
        async with db_session as sess:
            async with sess.begin():
                res = await sess.execute(sa.select(TrackerModel.tracker_id).where(TrackerModel.user_id == user_id,
                                                                                  cast(TrackerModel.track_end,
                                                                                       DATE) == datetime.date.today()))
        res.scalar_one_or_none()

        data = None
        if user_id == MAIN_USER_ID:
            data = TrackerCD(operation=operation, tracker_id=4)
        elif user_id == SECOND_USER_ID:
            data = TrackerCD(operation=operation, tracker_id=5)

        with expectation:
            assert data
            handler_result = await execute_callback_query_handler(user_id, data=data.pack())
            assert isinstance(handler_result, EditMessageText)
            assert handler_result.text == i18n.get(answer_text)
            assert handler_result.reply_markup == await _get_right_tracker_markup(user_id, redis_cli, buttons, i18n)
