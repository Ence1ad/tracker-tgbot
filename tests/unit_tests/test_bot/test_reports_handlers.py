from contextlib import nullcontext as does_not_raise
import pytest
from aiogram.methods import EditMessageText

from tests.unit_tests.utils import MAIN_USER_ID
from tgbot.keyboards.app_buttons import AppButtons


@pytest.mark.asyncio
class TestReportsHandlers:
    @pytest.mark.parametrize(
        "user_id, button_data, answer_text, expectation",
        [
            # (, AppButtons.general_data.REPORTS_BTN.name, 'options_text',
            #  does_not_raise()),
            (MAIN_USER_ID, AppButtons.general_data.REPORTS_BTN.name, 'options_text',
             does_not_raise()),
            # (SECOND_USER_ID, AppButtons.general_data.REPORTS_BTN.name, 'options_text',
            #  does_not_raise()),

        ]
    )
    async def test_get_report_options(
            self, user_id: int, expectation, execute_callback_query_handler, answer_text: str, redis_cli,
            i18n, buttons, button_data, db_session
    ):

        with expectation:
            handler_result = await execute_callback_query_handler(user_id, data=button_data)
            assert isinstance(handler_result, EditMessageText)