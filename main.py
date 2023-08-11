import asyncio
import logging

from aiogram.filters import Command
from aiogram import Dispatcher, Router

from config import bot
from tgbot import register_categories_handlers, register_actions_handlers

from tgbot.handlers.start import command_start_handler
from tgbot.utils.bot_commands import my_commands

router = Router()


async def start_bot(tgbot):
    await my_commands(tgbot)


async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    await start_bot(bot)
    dp.include_router(router)
    router.message.register(command_start_handler, Command("start"))
    register_categories_handlers(router)
    register_actions_handlers(router)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
