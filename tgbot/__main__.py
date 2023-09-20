import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings
from db.db_session import create_async_session
from tgbot.handlers import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.middlewares import SchedulerMiddleware, DbSessionMiddleware, CacheMiddleware
from tgbot.middlewares.button_middleware import ButtonsMiddleware
from tgbot.middlewares.translation_middleware import TranslatorRunnerMiddleware
from tgbot.schedule.schedule_adjustment import setup_scheduler
from tgbot.schedule.schedule_jobs import interval_sending_reports_job

from tgbot.utils.bot_commands import my_commands


async def start_bot(bot: Bot) -> None:
    await my_commands(bot)


async def main() -> None:
    # Initialize sqlalchemy session
    async_session: async_sessionmaker[AsyncSession] = await create_async_session(url=settings.db_url, echo=False)
    # Initialize bot
    bot: Bot = Bot(settings.BOT_TOKEN, parse_mode='html')
    # Initialize redis
    redis_client: Redis = Redis(connection_pool=settings.create_redis_pool)
    storage = RedisStorage(redis=redis_client)
    # Dispatcher is a root router
    dp = Dispatcher(storage=storage)
    # Get commands
    await start_bot(bot)
    # Initialize apscheduler
    scheduler = await setup_scheduler(bot=bot, jobstores=settings.scheduler_job_stores, redis_client=redis_client,
                                      storage=storage, async_session=async_session)

    await interval_sending_reports_job(scheduler=scheduler)
    # Initialize apscheduler
    buttons = AppButtons()

    translator = Translator()
    # Register middlewares
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(CacheMiddleware(redis_client))
    dp.callback_query.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(ButtonsMiddleware(buttons))
    dp.update.middleware.register(TranslatorRunnerMiddleware(translator.t_hub))
    # Register handlers
    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()
    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)

    try:
        scheduler.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as ex:
        logging.error(ex)
    finally:
        await dp.storage.close()
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=settings.LEVEL,
                        format=settings.FORMAT,
                        )
    logging.getLogger('apscheduler').setLevel(settings.LEVEL)
    asyncio.run(main())
