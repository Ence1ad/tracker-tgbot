import asyncio
import logging

import redis.asyncio as redis
from redis.asyncio import Redis

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Dispatcher, Bot

from config import settings
from tgbot.handlers import register_common_handlers


async def main() -> None:
    # Initialize bot
    bot: Bot = Bot(settings.BOT_TOKEN, parse_mode='html')
    # Initialize redis
    redis_client: Redis = redis.from_url(settings.cache_url)

    # Initialize redis storage
    storage: RedisStorage = RedisStorage(redis=redis_client)

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
