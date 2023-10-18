import asyncio
import logging

import redis.asyncio as redis
from aiogram.exceptions import TelegramAPIError
from redis.asyncio import Redis

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Dispatcher, Bot
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings
from db.db_session import create_async_session
from tgbot.handlers import register_common_handlers
from tgbot.handlers.categories_handlers import register_categories_handlers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.localization.localize import Translator
from tgbot.middlewares.apscheduler_middleware import SchedulerMiddleware
from tgbot.middlewares.button_middleware import ButtonsMiddleware
from tgbot.middlewares.chat_member_middleware import ChatMemberMiddleware
from tgbot.middlewares.db_middleware import DbSessionMiddleware
from tgbot.middlewares.redis_middleware import CacheMiddleware
from tgbot.middlewares.throttling_middleware import ThrottlingMiddleware
from tgbot.middlewares.translation_middleware import TranslatorRunnerMiddleware
from tgbot.schedule.schedule_adjustment import setup_scheduler
from tgbot.utils.before_bot_start import start_bot, is_bot_admin


async def main() -> None:
    """Initialize and run the Telegram bot along with necessary components and settings.

    This function serves as the entry point for running the Telegram bot. It initializes
    the bot, creates an SQLAlchemy session, sets up Redis storage, configures various
    components such as buttons, translator, and scheduler, and registers middlewares and
    handlers for the bot's functionality. The bot is then started, and the main function
    enters a polling loop to handle incoming updates.

    Note:
    ----
        Before running the bot, make sure to set up the required environment variables
        and bot token.

    :return: None
    """
    # Initialize bot
    bot: Bot = Bot(settings.BOT_TOKEN, parse_mode='html')

    # Initialize sqlalchemy session
    async_session: async_sessionmaker[AsyncSession] = await create_async_session(
        url=settings.db_url, echo=True
    )

    # Initialize redis
    redis_client: Redis = redis.from_url(settings.cache_url)

    # Initialize redis storage
    storage: RedisStorage = RedisStorage(redis=redis_client)

    # Initialize buttons
    buttons = AppButtons()

    # Initialize translator
    translator = Translator()

    # Initialize scheduler
    scheduler = await setup_scheduler(bot=bot, jobstores=settings.scheduler_job_stores,
                                      redis_client=redis_client, storage=storage,
                                      async_session=async_session)
    # Initialize dispatcher
    dp: Dispatcher = Dispatcher(storage=storage)

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

    dp.startup.register(start_bot)
    # Register middlewares
    dp.update.middleware.register(ButtonsMiddleware(buttons))
    dp.update.middleware.register(CacheMiddleware(redis_client))
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.update.middleware.register(TranslatorRunnerMiddleware(translator))
    dp.update.middleware.register(ChatMemberMiddleware())
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(ThrottlingMiddleware(
        limit=settings.THROTTLING_RATE_LIMIT,
        period=settings.THROTTLING_RATE_PERIOD)
    )
    # Register handlers
    common_handlers_router = register_common_handlers()
    categories_router = register_categories_handlers()
    dp.include_routers(common_handlers_router, categories_router)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=settings.LEVEL,
                        format=settings.FORMAT,
                        )
    logging.getLogger('apscheduler').setLevel(settings.LEVEL)
    asyncio.run(main())
