import asyncio
import logging

import redis.asyncio as redis
from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler_di import ContextSchedulerDecorator
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings
from db.db_session import create_async_session
from tgbot.handlers import register_common_handlers, register_actions_handlers, \
    register_categories_handlers, register_tracker_handlers, register_report_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.middlewares import SchedulerMiddleware, ButtonsMiddleware, \
    ChatMemberMiddleware, DbSessionMiddleware, CacheMiddleware, ThrottlingMiddleware, \
    TranslatorRunnerMiddleware
from tgbot.schedule.schedule_adjustment import setup_scheduler
from tgbot.schedule.schedule_jobs import interval_sending_reports_job
from tgbot.utils.before_bot_start import start_bot, is_bot_admin


async def _register_middlewares(
        dp: Dispatcher, async_session: async_sessionmaker[AsyncSession],
        buttons: AppButtons, redis_client: Redis, translator: Translator,
        scheduler: ContextSchedulerDecorator, throttling: tuple
) -> None:
    """Register middlewares in the Dispatcher.

    This function registers various middlewares in the given Dispatcher, including
    ButtonsMiddleware,nCacheMiddleware, DbSessionMiddleware, TranslatorRunnerMiddleware,
    ChatMemberMiddleware, and ThrottlingMiddleware.

    :param dp: Dispatcher: The aiogram Dispatcher instance for handling updates and
    events.
    :param async_session: async_sessionmaker[AsyncSession]: The SQLAlchemy asynchronous
     session.
    :param buttons: AppButtons: The instance of AppButtons class for managing custom
    keyboard buttons.
    :param redis_client: Redis: The Redis client for caching and storing data.
    :param translator: Translator: The translator for localization and
    internationalization of messages.
    :param scheduler: ContextSchedulerDecorator: The context scheduler for managing
    scheduled jobs.
    :param throttling: tuple: A tuple specifying the rate limit and period for
    throttling messages.
    :return:
    """
    dp.update.middleware.register(ButtonsMiddleware(buttons))
    dp.update.middleware.register(CacheMiddleware(redis_client))
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(TranslatorRunnerMiddleware(translator))
    dp.update.middleware.register(ChatMemberMiddleware())
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(ThrottlingMiddleware(limit=throttling[0],
                                                       period=throttling[1]))
    return None


async def _register_handlers(dp: Dispatcher) -> None:
    """Register routers and handlers in the Dispatcher.

    This function registers different routers and handlers in the given Dispatcher.
    It includes common, category, action, tracker, and report routers with their
    respective handlers.

    :param dp: Dispatcher: The aiogram Dispatcher instance for handling updates and
     events.
    :return: None
    """
    common_handlers_router = register_common_handlers()
    categories_router = register_categories_handlers()
    actions_router = register_actions_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()
    dp.include_routers(common_handlers_router, categories_router, actions_router,
                       tracker_router, report_router)
    return None


async def main(bot: Bot, debug: bool) -> None:
    """Initialize and run the Telegram bot application.

    This function sets up and runs a Telegram bot with the provided configurations and
    middleware. It registers various handlers, including common, category, action,
    tracker, and report handlers, and initializes a scheduler for executing scheduled
    jobs. The bot interacts with users and handles messages, commands, and other
    actions.

    :param bot: Bot: The Telegram Bot instance for connecting to the Telegram API.
    :param debug: bool: A flag indicating whether the bot is running in debug mode.
    :return: None
    """
    # Initialize sqlalchemy session
    async_session: async_sessionmaker[AsyncSession] = await create_async_session(
        url=settings.db_url, echo=False
    )
    # Initialize redis
    redis_client: Redis = redis.from_url(settings.cache_url)
    # Initialize buttons
    buttons: AppButtons = AppButtons()
    # Initialize translator
    translator: Translator = Translator()
    # Initialize redis storage
    storage: RedisStorage = RedisStorage(redis=redis_client)
    # Initialize dispatcher
    dp: Dispatcher = Dispatcher(storage=storage)

    # Initialize scheduler
    scheduler: ContextSchedulerDecorator = await setup_scheduler(
        bot=bot, jobstores=settings.scheduler_job_stores,
        redis_client=redis_client, storage=storage,
        async_session=async_session
    )
    if not debug:
        try:
            await is_bot_admin(bot, settings.GROUP_ID)
        except (TelegramAPIError, PermissionError) as error:
            error_msg = f"Error with main group: {error}"
            try:
                await bot.send_message(settings.ADMIN_ID, error_msg)
            finally:
                logging.exception(error_msg)
                return

    # Get commands
    await start_bot(bot)

    # Set sending reports job
    await interval_sending_reports_job(scheduler=scheduler)
    # Register middlewares
    await _register_middlewares(
        dp=dp, async_session=async_session, buttons=buttons, redis_client=redis_client,
        throttling=(settings.THROTTLING_RATE_LIMIT, settings.THROTTLING_RATE_PERIOD),
        translator=translator, scheduler=scheduler
    )

    dp.startup.register(start_bot)
    # Register handlers
    await _register_handlers(dp=dp)

    try:
        if debug:
            await dp.emit_startup()
        else:
            scheduler.start()
            await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":

    logging.basicConfig(level=settings.LEVEL, format=settings.FORMAT)
    logging.getLogger('apscheduler').setLevel(settings.LEVEL)
    # Initialize bot
    bot_api: Bot = Bot(settings.BOT_TOKEN, parse_mode='html')
    asyncio.run(main(bot_api, debug=False))
