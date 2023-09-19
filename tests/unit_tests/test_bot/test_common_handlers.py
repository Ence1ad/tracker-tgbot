from contextlib import nullcontext as does_not_raise

import pytest
from aiogram import Dispatcher
from aiogram.methods import SendMessage, EditMessageText
from aiogram.types import User
from pytest_asyncio.plugin import SimpleFixtureFunction, FactoryFixtureFunction
from redis.asyncio import Redis
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_schedule_command import is_redis_sismember_user
from db import UserModel
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import new_user_text, user_in_db_text, started_tracker_text, options_text
from .utils import USER_ID


@pytest.mark.asyncio
class TestCommonHandlers:
    @pytest.mark.parametrize(
        "user_id, command, answer_text, expectation",
        [
            (USER_ID, '/start', new_user_text, does_not_raise()),  # add the user to the db and the redis set
            (USER_ID, '/start', None, does_not_raise()),  # checking the answer text when user tracker was launched
            (12345, '/start', new_user_text, does_not_raise()),  # add the user to the db and the redis set
            (12345, '/start', user_in_db_text, does_not_raise()),  # check the user in the db and in the redis set
            (12345, '/start', new_user_text, pytest.raises(AssertionError)),
            (USER_ID, '/help', new_user_text, pytest.raises(AssertionError)),
            # (USER_ID, '/start', None, pytest.raises(AssertionError)),
            (USER_ID, None, new_user_text, pytest.raises(AssertionError)),
            (USER_ID, '/start', '', pytest.raises(AssertionError)),

        ]
    )
    @pytest.mark.asyncio
    async def test_command_start_handler(
            self, get_tracker: SimpleFixtureFunction, user_id: int, answer_text: str, command: str, expectation: does_not_raise,
            execute_message_handler: FactoryFixtureFunction, bot_db_session: async_sessionmaker[AsyncSession],
            redis_cli: Redis, buttons: AppButtons,
    ):
        handler_returns = await execute_message_handler(user_id=user_id, command=command)
        if answer_text is None:
            answer_text = await started_tracker_text(user_id, redis_cli)
        with expectation:

            assert isinstance(handler_returns, SendMessage)

            assert handler_returns.text == answer_text
            assert handler_returns.reply_markup == await start_menu_inline_kb(await buttons.main_menu_buttons())
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
            (USER_ID, AppButtons.general_data.EXIT_BTN.name, options_text, pytest.raises(AssertionError)),
            (USER_ID, AppButtons.general_data.CANCEL_BTN.name, None, pytest.raises(AssertionError)),
            (12345, AppButtons.general_data.EXIT_BTN.name, options_text, does_not_raise()),
            (12345, None, options_text, pytest.raises(AssertionError)),
        ]
    )
    async def test_exit_menu_handler(self, get_tracker: SimpleFixtureFunction,
                                     execute_callback_query_handler: FactoryFixtureFunction,
                                     redis_cli: Redis,
                                     user_id: int, answer_text: str, data: str, expectation: does_not_raise,
                                     buttons: AppButtons):
        handler_returns = await execute_callback_query_handler(user_id, data)
        if answer_text is None:
            answer_text = await started_tracker_text(user_id, redis_cli)
        with expectation:
            assert isinstance(handler_returns, EditMessageText)
            assert handler_returns.text == answer_text
            assert handler_returns.reply_markup == await start_menu_inline_kb(await buttons.main_menu_buttons())
            user_in_cache = await is_redis_sismember_user(user_id, redis_client=redis_cli)
            assert user_in_cache is True
