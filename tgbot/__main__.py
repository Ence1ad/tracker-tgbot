import asyncio
import logging

import redis.asyncio as redis
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# # Construct an absolute path to the project's root directory
# project_root = Path(__file__).parent.parent.as_posix()
#
# # Add the project's root directory to sys.path
# sys.path.append(project_root)
from config import settings
from handlers.common_handles import register_common_handlers
from handlers.tracker_handlers import register_tracker_handlers
from handlers.reports_handlers import register_report_handlers
from handlers.actions_handlers import register_actions_handlers
from handlers.categories_handlers import register_categories_handlers


from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.middlewares import SchedulerMiddleware, DbSessionMiddleware, CacheMiddleware, \
    ButtonsMiddleware, ChatMemberMiddleware, TranslatorRunnerMiddleware
from tgbot.schedule.schedule_adjustment import setup_scheduler
from tgbot.schedule.schedule_jobs import interval_sending_reports_job
from tgbot.utils.bot_commands import my_commands

from db.db_session import create_async_session


async def start_bot(bot: Bot) -> None:
    await my_commands(bot)


async def main() -> None:
    # Initialize sqlalchemy session
    async_session: async_sessionmaker[AsyncSession] = await create_async_session(url=settings.db_url, echo=False)

    # Initialize bot
    bot: Bot = Bot(settings.BOT_TOKEN, parse_mode='html')

    # Initialize redis
    redis_client: Redis = redis.from_url(settings.cache_url)

    # redis_client: Redis = Redis(connection_pool=settings.create_redis_pool)
    storage: RedisStorage = RedisStorage(redis=redis_client)

    # Initialize apscheduler
    translator = Translator()

    # Initialize buttons
    buttons = AppButtons()

    # Initialize scheduler
    scheduler = await setup_scheduler(bot=bot, jobstores=settings.scheduler_job_stores, redis_client=redis_client,
                                      storage=storage, async_session=async_session,
                                      # t_hub=translator.t_hub
                                      )
    # Initialize dispatcher
    dp: Dispatcher = Dispatcher(storage=storage)
    # Get commands
    await start_bot(bot)

    await interval_sending_reports_job(scheduler=scheduler)

    # Register middlewares
    dp.update.middleware.register(ButtonsMiddleware(buttons))
    dp.update.middleware.register(CacheMiddleware(redis_client))
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(TranslatorRunnerMiddleware(translator))
    dp.update.middleware.register(ChatMemberMiddleware())
    dp.callback_query.middleware.register(SchedulerMiddleware(scheduler))

    # Register handlers
    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()
    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)

    try:
        scheduler.start()
        await dp.start_polling(bot)
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
