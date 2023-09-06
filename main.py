import asyncio
import logging

from aiogram import Dispatcher, Bot

from sqlalchemy.ext.asyncio import create_async_engine

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apscheduler_di import ContextSchedulerDecorator
from db.db_session import create_async_session
from settings import DB_URL, redis_client, BOT, scheduler_jobstores
from tgbot import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers
from tgbot.middlewares.apschedulermiddleware import SchedulerMiddleware
from tgbot.middlewares.dbmiddleware import DbSessionMiddleware
from tgbot.schedul.schedule_jobs import schedule_weekly_report, interval_sending_reports_job

from tgbot.utils.bot_commands import my_commands
from aiogram.fsm.storage.redis import RedisStorage


async def start_bot(tgbot):
    await my_commands(tgbot)


async def main() -> None:
    async_engine = create_async_engine(url=DB_URL, echo=False, pool_size=10, max_overflow=10)
    async_session = await create_async_session(async_engine)

    # Dispatcher is a root router
    dp = Dispatcher(storage=RedisStorage(redis=redis_client))
    # Get commands
    await start_bot(BOT)

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=scheduler_jobstores))
    scheduler.ctx.add_instance(BOT, declared_class=Bot)

    await interval_sending_reports_job(scheduler=scheduler)

    # Register middlewares
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    # Register handlers
    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()

    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)

    try:
        scheduler.start()
        await dp.start_polling(BOT)
    except Exception as ex:
        logging.error(ex)
    finally:
        await dp.storage.close()
        await async_engine.dispose()
        scheduler.shutdown()
        await BOT.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    asyncio.run(main(), debug=True)
