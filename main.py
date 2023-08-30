import asyncio
import logging


from aiogram import Dispatcher, Router

# from aiogram.fsm.storage import redis
# from redis.asyncio.client import Redis

from cache.redis_cache import redis_client
from config import bot
from tgbot import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers

from tgbot.utils.bot_commands import my_commands
from aiogram.fsm.storage.redis import RedisStorage



async def start_bot(tgbot):
    await my_commands(tgbot)


async def main() -> None:
    # pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    # redis_client = Redis(connection_pool=pool)
    # Dispatcher is a root router
    dp = Dispatcher(storage=RedisStorage(redis=redis_client))
    await start_bot(bot)

    # Register handlers
    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()

    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(), debug=True)
