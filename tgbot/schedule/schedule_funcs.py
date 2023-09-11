import asyncio

from aiogram import Bot
from aiogram.types import FSInputFile
from pandas import DataFrame
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_commands import redis_delete_tracker, redis_hget_tracker_data, redis_get_members
from data_preparation.create_report import create_fig
from data_preparation.pd_prepare import pd_action_data, pd_category_data
from db.report.report_commands import get_report
from db.tracker.tracker_db_command import delete_tracker
from tgbot.utils.answer_text import too_long_tracker, xlsx_title


async def schedule_delete_tracker(bot: Bot, user_id, redis_client: Redis,
                                  async_session: async_sessionmaker[AsyncSession]):
    tracker_id = await redis_hget_tracker_data(user_id, redis_client, 'tracker_id')
    # db_session = await sa_session()
    if tracker_id:
        action_name = (await redis_hget_tracker_data(user_id, redis_client, 'action_name')).decode(encoding='utf-8')
        await delete_tracker(user_id, tracker_id=int(tracker_id), db_session=async_session)
        await redis_delete_tracker(user_id, redis_client)
        await bot.send_message(chat_id=user_id, text=f'The tracker - {action_name} {too_long_tracker}')


async def schedule_weekly_report(bot: Bot, redis_client: Redis, async_session: async_sessionmaker[AsyncSession]):
    members = await redis_get_members(redis_client)
    for user_id in members:
        report = await get_report(int(user_id), db_session=async_session)
        if report:
            action_data: DataFrame = await pd_action_data(report)
            category_data: DataFrame = await pd_category_data(report)
            await create_fig(df_action=action_data, df_categories=category_data)
            await asyncio.sleep(3)
            document = FSInputFile(xlsx_title)
            await bot.send_document(chat_id=user_id, document=document)
            await asyncio.sleep(2)
