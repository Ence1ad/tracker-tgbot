import datetime
from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest
import sqlalchemy as sa
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.methods import SendMessage, EditMessageText, SendDocument
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import cast, DATE
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_utils import set_redis_name
from cache.trackers_redis_manager import is_redis_hexists_tracker, \
    redis_get_user_day_trackers, \
    redis_incr_user_day_trackers, redis_hget_tracker_data, TRACKER_CNT_PREFIX
from config import settings
from db import TrackerModel
from db.operations.actions_operations import select_category_actions
from db.operations.categories_operations import select_categories
from db.operations.report_operations import select_weekly_trackers
from db.operations.tracker_operations import select_stopped_trackers, \
    select_tracker_duration
from tests.integration.mocked_bot import MockedBot
from tests.integration.test_bot.utils import TEST_CHAT
from tests.utils import MAIN_USER_ID, OTHER_USER_ID, USER_ID_WITH_TRACKER_LIMIT
from tgbot.handlers.categories_handlers.read_categories import _get_operation
from tgbot.handlers.tracker_handlers.delete_tracker import _get_right_tracker_markup
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation, ActionCD, \
    TrackerOperation, TrackerCD
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.states import TrackerState
from tgbot.utils.tracker_info import started_tracker_info


@pytest.mark.usefixtures('add_data_to_db', 'create_tracker_fixt')
@pytest.mark.asyncio
class TestActionsHandlers:
    USER_WITHOUT_TRACKER = OTHER_USER_ID
    USER_WITHOUT_CATEGORIES = 55555

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT,
             AppButtons.general_btn_source.TRACKERS_BTN.name,
             'started_tracker_title', does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.TRACKERS_BTN.name,
             'options_text', does_not_raise()),
            (USER_WITHOUT_TRACKER,
             AppButtons.trackers_btn_source.DURATION_TRACKER_BTN.name, 'options_text',
             does_not_raise()),

        ]
    )
    async def test_trackers_main_menu_handler(
            self, user_id: int, expectation: Any, button_data: str,
            execute_callback_query_handler, answer_text: str,
            redis_cli: Redis, i18n: TranslatorRunner, buttons: AppButtons,
    ) -> None:

        is_tracker = await is_redis_hexists_tracker(user_id=user_id,
                                                    redis_client=redis_cli)
        print(is_tracker)
        with expectation:

            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, SendMessage)
            if is_tracker:
                started_tracker_txt = await started_tracker_info(
                    user_id=int(user_id), redis_client=redis_cli, i18n=i18n,
                    title=answer_text
                )
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
            (MAIN_USER_ID, AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'select_category_text', does_not_raise()),
            (USER_ID_WITH_TRACKER_LIMIT,
             AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'tracker_daily_limit_text', does_not_raise()),
            (USER_WITHOUT_TRACKER,
             AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'select_category_text', does_not_raise()),
            (USER_WITHOUT_CATEGORIES,
             AppButtons.trackers_btn_source.START_TRACKER_BTN.name,
             'empty_categories_text', does_not_raise()),
        ]
    )
    async def test_pass_tracker_checks(
            self, user_id: int, expectation: Any, button_data: str,
            execute_callback_query_handler, answer_text: str,
            redis_cli: Redis, i18n: TranslatorRunner, buttons: AppButtons,
            db_session_fixture: AsyncSession, db_user_factory
    ) -> None:
        await db_user_factory(user_id)
        is_tracker = await is_redis_hexists_tracker(user_id=user_id,
                                                    redis_client=redis_cli)
        if is_tracker and USER_ID_WITH_TRACKER_LIMIT:
            for _ in range(settings.USER_TRACKERS_DAILY_LIMIT):
                await redis_incr_user_day_trackers(user_id, redis_client=redis_cli)
        user_trackers_cnt = await redis_get_user_day_trackers(user_id, redis_cli)
        print(user_trackers_cnt)
        handler_result = await execute_callback_query_handler(user_id, data=button_data)
        with expectation:
            assert isinstance(handler_result, (EditMessageText, SendMessage))
            if user_trackers_cnt is None or (
                    int(user_trackers_cnt) < settings.USER_TRACKERS_DAILY_LIMIT):
                if categories := await select_categories(user_id, db_session_fixture):
                    operation = await _get_operation(call_data=button_data,
                                                     buttons=buttons)
                    assert handler_result.text == i18n.get(answer_text)
                    assert handler_result.reply_markup == await callback_factories_kb(
                        categories, operation)
                else:
                    assert handler_result.text == i18n.get(answer_text)
                    assert handler_result.reply_markup == await menu_inline_kb(
                        await buttons.categories_btn_source.new_category(), i18n
                    )
            else:
                print('Здесь')
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER,
             'select_category_4_tracker', does_not_raise()),
            (USER_ID_WITH_TRACKER_LIMIT, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER, 'select_category_4_tracker',
             does_not_raise()),
            (USER_WITHOUT_TRACKER, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER, 'select_category_4_tracker',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER, 'valid_data_text', does_not_raise()),
        ]
    )
    async def test_take_action_4_tracker(
            self, user_id: int, expectation, execute_callback_query_handler,
            answer_text: str, i18n: TranslatorRunner, buttons: AppButtons,
            db_session_fixture: AsyncSession, state: FSMContext, operation: Any,
            db_category_factory
    ) -> None:
        if user_id == TestActionsHandlers.USER_WITHOUT_CATEGORIES:
            await db_category_factory(user_id)
        categories_lst = await select_categories(user_id, db_session_fixture)
        category_id = categories_lst[0].category_id
        category_name = categories_lst[0].category_name
        data = CategoryCD(operation=operation, category_id=category_id,
                          category_name=category_name)

        actions = await select_category_actions(
            user_id, category_id=category_id, db_session=db_session_fixture
        )
        handler_result = await execute_callback_query_handler(
            user_id, data=data.pack(), state=state
        )
        with expectation:
            assert isinstance(handler_result, (EditMessageText, SendMessage))
            if actions:
                assert handler_result.text == i18n.get(answer_text,
                                                       category_name=category_name,
                                                       new_line='\n')
                assert handler_result.reply_markup == await callback_factories_kb(
                    actions, operation)
            else:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.general_btn_source.main_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, state, operation, answer_text, expectation",
        [
            (
                    MAIN_USER_ID, TrackerState.WAIT_CATEGORY_DATA,
                    ActionOperation.READ_TRACKER,
                    'new_tracker_text', does_not_raise()),
            (USER_ID_WITH_TRACKER_LIMIT, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER,
             'not_enough_data_text', does_not_raise()),
            (OTHER_USER_ID, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER, 'new_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, TrackerState.WAIT_CATEGORY_DATA,
             ActionOperation.READ_TRACKER,
             'new_tracker_text', pytest.raises(AssertionError)),
            # this user don't have an actions
        ]
    )
    async def test_create_tracker(
            self, user_id: int, expectation, execute_callback_query_handler,
            answer_text: str, redis_cli: Redis, i18n: TranslatorRunner,
            buttons: AppButtons, db_session_fixture: AsyncSession, state: FSMContext,
            operation: Any, dispatcher: Dispatcher, bot: MockedBot
    ):
        key = StorageKey(bot_id=bot.id, chat_id=TEST_CHAT.id, user_id=user_id)
        state_data = await dispatcher.fsm.storage.get_data(key)
        category_id = state_data.get('category_id')
        data = action_name = None
        actions = await select_category_actions(user_id, category_id=category_id,
                                                db_session=db_session_fixture)
        if actions:
            action_id = actions[0].action_id
            action_name = actions[0].action_name
            data = ActionCD(operation=operation, action_id=action_id,
                            action_name=action_name)
        before_handler = await is_redis_hexists_tracker(user_id, redis_cli)

        with expectation:
            assert actions
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=data.pack(),
                                                                  state=state)
            assert isinstance(handler_result, EditMessageText)
            after_handler = await is_redis_hexists_tracker(user_id, redis_cli)
            if before_handler == after_handler:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)
            else:
                name = set_redis_name(user_id, prefix=TRACKER_CNT_PREFIX)
                assert await redis_cli.get(
                    name)  # check the redis_expireat_midnight func was started
                assert await redis_incr_user_day_trackers(user_id, redis_cli)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
                assert handler_result.text == i18n.get(answer_text,
                                                       action_name=action_name)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name,
             'answer_stop_tracker_text',
             does_not_raise()),
            (OTHER_USER_ID, AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name,
             'answer_stop_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES,
             AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name,
             'not_launched_tracker_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_check_is_launched_tracker(
            self, user_id: int, expectation: Any, execute_callback_query_handler,
            answer_text: str, redis_cli: Redis, i18n: TranslatorRunner,
            buttons: AppButtons, button_data,
    ) -> None:
        is_tracker = await is_redis_hexists_tracker(user_id, redis_cli)

        with expectation:
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, SendMessage)
            if is_tracker:
                started_tracker = await started_tracker_info(
                    user_id=user_id, redis_client=redis_cli, i18n=i18n,
                    title='started_tracker_title'
                )
                assert handler_result.text[:20] == (started_tracker + i18n.get(
                    answer_text))[:20]
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
            (OTHER_USER_ID, AppButtons.general_btn_source.NO_BTN.name, 'options_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES, AppButtons.general_btn_source.NO_BTN.name,
             'options_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_stop_tracker_no_handler(
            self, user_id: int, expectation: Any, execute_callback_query_handler,
            answer_text: str, i18n: TranslatorRunner, buttons: AppButtons, button_data,
    ) -> None:
        with expectation:
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, EditMessageText)
            assert handler_result.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (MAIN_USER_ID, AppButtons.general_btn_source.YES_BTN.name,
             'stop_tracker_text', does_not_raise()),
            (OTHER_USER_ID, AppButtons.general_btn_source.YES_BTN.name,
             'stop_tracker_text', does_not_raise()),
            # this user don't have an actions
            (USER_WITHOUT_CATEGORIES, AppButtons.general_btn_source.YES_BTN.name,
             'not_launched_tracker_text', does_not_raise()),
        ]
    )
    async def test_stop_tracker_yes_handler(
            self, user_id: int, expectation: Any, execute_callback_query_handler,
            answer_text: str, redis_cli: Redis, i18n: TranslatorRunner,
            buttons: AppButtons, button_data, db_session_fixture: AsyncSession
    ) -> None:

        tracker_id = await redis_hget_tracker_data(user_id, redis_cli, 'tracker_id')
        print(tracker_id)
        if tracker_id:
            track_text = await started_tracker_info(
                user_id=user_id, redis_client=redis_cli, i18n=i18n,
                title=answer_text
            )
        with expectation:
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, EditMessageText)
            if tracker_id:

                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_start(), i18n)
                assert handler_result.text[:20] == track_text[:20]
                assert not await is_redis_hexists_tracker(user_id, redis_cli)
                assert await select_tracker_duration(user_id=user_id,
                                                     tracker_id=int(tracker_id),
                                                     db_session=db_session_fixture) != 0
            else:
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
                assert handler_result.text == i18n.get(answer_text)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT,
             AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name,
             'empty_stopped_tracker_text',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name,
             'daily_tracker_text',
             does_not_raise()),
            (OTHER_USER_ID, AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name,
             'daily_tracker_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES,
             AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name,
             'empty_stopped_tracker_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_take_traker_4_delete(
            self, user_id: int, expectation: Any, execute_callback_query_handler,
            answer_text: str, redis_cli: Redis, i18n: TranslatorRunner,
            buttons: AppButtons, button_data, db_session_fixture: AsyncSession
    ) -> None:

        stopped_trackers = await select_stopped_trackers(user_id, db_session_fixture)
        with expectation:
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, (EditMessageText, SendMessage))
            if stopped_trackers:
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await callback_factories_kb(
                    stopped_trackers,
                    enum_val=TrackerOperation.DEL)
            else:
                assert handler_result.text == i18n.get(answer_text)
                await _get_right_tracker_markup(user_id, redis_cli, buttons, i18n)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT, AppButtons.general_btn_source.REPORTS_BTN.name,
             'options_text',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_btn_source.REPORTS_BTN.name,
             'options_text',
             does_not_raise()),
            (OTHER_USER_ID, AppButtons.general_btn_source.REPORTS_BTN.name,
             'options_text',
             does_not_raise()),

        ]
    )
    async def test_main_menu_reports_handler(
            self, user_id: int, expectation: Any, execute_callback_query_handler,
            answer_text: str, i18n: TranslatorRunner, buttons: AppButtons, button_data
    ) -> None:
        with expectation:
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, EditMessageText)
            assert handler_result.text == i18n.get(answer_text)
            assert handler_result.reply_markup == await menu_inline_kb(
                await buttons.reports_btn_source.report_menu(),
                i18n)

    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            (USER_ID_WITH_TRACKER_LIMIT,
             AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name,
             'empty_trackers_text',
             does_not_raise()),
            (MAIN_USER_ID, AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name,
             'send_report_text',
             does_not_raise()),
            (OTHER_USER_ID, AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name,
             'send_report_text',
             does_not_raise()),
            (USER_WITHOUT_CATEGORIES,
             AppButtons.reports_btn_source.WEEKLY_REPORT_BTN.name,
             'empty_trackers_text',
             does_not_raise()),  # this user don't have an actions
        ]
    )
    async def test_get_weekly_report(
            self, user_id: int, expectation: Any, execute_callback_query_handler,
            answer_text: str, i18n: TranslatorRunner, buttons: AppButtons,
            button_data, db_session_fixture: AsyncSession
    ) -> None:
        report = await select_weekly_trackers(user_id, db_session_fixture)
        with expectation:
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=button_data)
            assert isinstance(handler_result, (EditMessageText, SendDocument))
            if report and isinstance(handler_result, SendDocument):
                assert handler_result.document.filename == \
                       settings.WEEKLY_XLSX_FILE_NAME
                assert handler_result.caption == i18n.get(answer_text)
            elif not report and isinstance(handler_result, EditMessageText):
                assert handler_result.text == i18n.get(answer_text)
                assert handler_result.reply_markup == await menu_inline_kb(
                    await buttons.general_btn_source.main_menu_buttons(), i18n)

    @pytest.mark.parametrize(
        "user_id, operation, answer_text, expectation",
        [
            (MAIN_USER_ID, TrackerOperation.DEL, 'delete_tracker_text',
             does_not_raise()),
            (MAIN_USER_ID, TrackerOperation.DEL, 'already_delete_tracker_text',
             does_not_raise()),
            (OTHER_USER_ID, TrackerOperation.DEL, 'delete_tracker_text',
             does_not_raise()),
            (OTHER_USER_ID, TrackerOperation.DEL, 'already_delete_tracker_text',
             does_not_raise()),
        ]
    )
    async def test_delete_tracker_handler(
            self, user_id: int, expectation, execute_callback_query_handler,
            answer_text: str, redis_cli: Redis, i18n: TranslatorRunner,
            buttons: AppButtons, db_session_fixture: AsyncSession, operation
    ) -> None:
        async with db_session_fixture as sess:
            async with sess.begin():
                res = await sess.execute(sa.select(TrackerModel.tracker_id).where(
                    TrackerModel.user_id == user_id,
                    cast(TrackerModel.track_end,
                         DATE) == datetime.date.today()))
        res.scalar_one_or_none()

        data = None
        if user_id == MAIN_USER_ID:
            data = TrackerCD(operation=operation, tracker_id=4)
        elif user_id == OTHER_USER_ID:
            data = TrackerCD(operation=operation, tracker_id=5)

        with expectation:
            assert data
            handler_result = await execute_callback_query_handler(user_id,
                                                                  data=data.pack())
            assert isinstance(handler_result, EditMessageText)
            assert handler_result.text == i18n.get(answer_text)
            assert handler_result.reply_markup == await _get_right_tracker_markup(
                user_id, redis_cli, buttons, i18n)
