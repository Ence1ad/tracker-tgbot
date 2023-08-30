import asyncio
import logging


from aiogram import Dispatcher

from sqlalchemy.ext.asyncio import create_async_engine


from db.db_session import create_async_session
from settings import BOT, DB_URL, redis_client
from tgbot import register_common_handlers, register_actions_handlers, register_categories_handlers, \
    register_tracker_handlers, register_report_handlers
from tgbot.middlewares.middleware import DbSessionMiddleware

from tgbot.utils.bot_commands import my_commands
from aiogram.fsm.storage.redis import RedisStorage


async def start_bot(tgbot):
    await my_commands(tgbot)


async def main() -> None:

    async_engine = create_async_engine(url=DB_URL, echo=False, pool_size=10, max_overflow=20)
    async_session = await create_async_session(async_engine)

    # Dispatcher is a root router
    dp = Dispatcher(storage=RedisStorage(redis=redis_client))
    await start_bot(BOT)
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    # Register handlers
    common_handlers_router = register_common_handlers()
    actions_router = register_actions_handlers()
    categories_router = register_categories_handlers()
    tracker_router = register_tracker_handlers()
    report_router = register_report_handlers()

    dp.include_routers(common_handlers_router, categories_router, actions_router, tracker_router, report_router)

    try:
        await dp.start_polling(BOT)
    except Exception as ex:
        logging.error(ex)
    finally:
        await BOT.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(), debug=True)
