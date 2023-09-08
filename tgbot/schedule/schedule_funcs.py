import asyncio

from aiogram import Bot
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from cache.redis_commands import redis_delete_tracker, redis_hget_tracker_data, redis_get_members
from data_preparation.create_report import create_bar
from data_preparation.pd_prepare import pd_data
from db.report.report_commands import get_report
from db.tracker.tracker_db_command import delete_tracker
from settings import DB_URL, BOT
from tgbot.utils.answer_text import too_long_tracker, xlsx_title


async def sa_session():
    async_engine = create_async_engine(url=DB_URL, echo=False, pool_size=10, max_overflow=10)
    db_session = AsyncSession(async_engine)
    return db_session


async def schedule_delete_tracker(bot: Bot, user_id):
    tracker_id = await redis_hget_tracker_data(user_id, 'tracker_id')
    db_session = await sa_session()
    if tracker_id:
        action_name = (await redis_hget_tracker_data(user_id, 'action_name')).decode(encoding='utf-8')
        await delete_tracker(user_id, tracker_id=int(tracker_id), db_session=db_session)
        await redis_delete_tracker(user_id)
        await bot.send_message(chat_id=user_id, text=f'The tracker - {action_name} {too_long_tracker}')


async def schedule_weekly_report():
    db_session = await sa_session()
    members = await redis_get_members()
    for user_id in members:
        report = await get_report(int(user_id), db_session)
        if report:
            data = await pd_data(report)
            await create_bar(rows=data, max_col=len(data) + 1)
            await asyncio.sleep(3)
            document = FSInputFile(xlsx_title)
            await BOT.send_document(chat_id=user_id, document=document)
            await asyncio.sleep(2)
