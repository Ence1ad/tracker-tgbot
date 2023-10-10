import asyncio
import logging

import redis.asyncio as redis
from redis.asyncio import Redis

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Dispatcher, Bot
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings
from db.db_session import create_async_session
from tgbot.handlers import register_common_handlers
from tgbot.schedule.schedule_adjustment import setup_scheduler


async def main() -> None:
    # Initialize bot
    bot: Bot = Bot(settings.BOT_TOKEN, parse_mode='html')

    # Initialize sqlalchemy session
    async_session: async_sessionmaker[AsyncSession] = await create_async_session(url=settings.db_url, echo=True)

    # Initialize redis
    redis_client: Redis = redis.from_url(settings.cache_url)

    # Initialize redis storage
    storage: RedisStorage = RedisStorage(redis=redis_client)

    # Initialize scheduler
    scheduler = await setup_scheduler(bot=bot, jobstores=settings.scheduler_job_stores,
                                      redis_client=redis_client, storage=storage, async_session=async_session)
    # Initialize dispatcher
    dp: Dispatcher = Dispatcher(storage=storage)

    # Register handlers
    common_handlers_router = register_common_handlers()
    dp.include_routers(common_handlers_router)

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
