from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest
from aiogram.enums import BotCommandScopeType
from aiogram.methods import SetMyCommands
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from apscheduler_di import ContextSchedulerDecorator
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.users_redis_manager import redis_sadd_user_id
from config import settings
from db.operations.tracker_operations import create_tracker, select_tracker_duration
from tests.integration.mocked_bot import MockedBot
from tests.utils import MAIN_USER_ID, CATEGORY_ID, ACTION_ID, OTHER_USER_ID
from tgbot.__main__ import main
from tgbot.schedule.schedule_funcs import schedule_delete_tracker, \
    schedule_weekly_report
from tgbot.schedule.schedule_jobs import interval_sending_reports_job
from tgbot.utils.before_bot_start import start_bot, is_bot_admin
from tgbot.utils.bot_commands import bot_commands, CommandName


@pytest.mark.asyncio
async def test_start_bot(bot: MockedBot) -> None:
    answer_message = await start_bot(bot)
    bot_name = await bot.get_my_name()
    text = f'The "{bot_name}" bot has been launched!'
    assert answer_message.chat_id == settings.ADMIN_ID
    assert answer_message.text == text


@pytest.mark.asyncio
async def test_bot_commands(bot: MockedBot) -> None:
    set_commands = await bot_commands(bot)
    assert isinstance(set_commands, SetMyCommands)
    assert set_commands.scope.type == BotCommandScopeType.ALL_PRIVATE_CHATS
    assert set_commands.language_code == settings.GLOBAL_LANG_CODE
    assert [com.command for com in set_commands.commands] == \
           [com.value for com in CommandName]


@pytest.mark.asyncio
async def test_is_bot_admin(bot: MockedBot) -> None:
    with pytest.raises(PermissionError):
        await is_bot_admin(bot, chat_id=settings.GROUP_ID)


@pytest.mark.asyncio
async def test_main_func(bot: MockedBot) -> None:
    await main(bot=bot, debug=True)


@pytest.mark.asyncio
class TestScheduleFunc:
    @pytest.mark.parametrize(
        "user_id, msg_text, expectation",
        [
            (MAIN_USER_ID, 'too_long_tracker', does_not_raise()),
            (34566678, 'too_long_tracker', does_not_raise()),
        ]
    )
    async def test_schedule_delete_tracker(
            self, bot: MockedBot, user_id: int, redis_cli: Redis, add_data_to_db,
            create_tracker_fixt_fact, db_category_factory,
            db_session_fixture: AsyncSession, msg_text: str, expectation: Any
    ) -> None:
        if user_id == MAIN_USER_ID:
            await create_tracker(user_id, category_id=CATEGORY_ID, action_id=ACTION_ID,
                                 db_session=db_session_fixture)
            await create_tracker_fixt_fact(user_id)
        else:
            await db_category_factory(user_id)
        with expectation:
            res = await schedule_delete_tracker(bot, user_id, redis_cli,
                                                db_session_fixture,
                                                msg_text)
            if user_id == MAIN_USER_ID:
                assert res
            else:
                assert not res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (OTHER_USER_ID, does_not_raise()),
        ]
    )
    async def test_schedule_weekly_report(
            self, bot: MockedBot, redis_cli: Redis, user_id: int, add_data_to_db,
            db_session_fixture: AsyncSession, expectation: Any,
            create_tracker_fixt_fact,
    ) -> None:
        await redis_sadd_user_id(user_id=user_id, redis_client=redis_cli)
        tracker_id = await create_tracker(user_id, category_id=CATEGORY_ID,
                                          action_id=ACTION_ID,
                                          db_session=db_session_fixture)
        await create_tracker_fixt_fact(user_id)
        await select_tracker_duration(user_id=user_id, tracker_id=int(str(tracker_id)),
                                      db_session=db_session_fixture)
        with expectation:
            await schedule_weekly_report(bot, redis_cli, db_session_fixture)

    async def test_interval_sending_reports_job(self,
                                                scheduler: ContextSchedulerDecorator):
        res: Job = await interval_sending_reports_job(scheduler)
        assert isinstance(res, Job)
        test_trigger = CronTrigger(day_of_week=settings.CRON_DAY_OF_WEEK,
                                   hour=settings.CRON_HOUR,
                                   minute=settings.CRON_MINUTE)
        assert res.trigger.FIELDS_MAP == test_trigger.FIELDS_MAP
        assert res.pending
