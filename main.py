import asyncio
import logging

from aiogram.filters import Command
from aiogram import Dispatcher, Router, F

from config import bot
from tgbot.handlers import register_categories_handlers, register_actions_handlers, register_tracker_handlers,\
     register_report_handlers
from tgbot.handlers.exit_handler import exit_menu

from tgbot.handlers.start import command_start_handler
from tgbot.keyboards.buttons_names import exit_btn
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
    router.callback_query.register(exit_menu, F.data == exit_btn)
    register_categories_handlers(router)
    register_actions_handlers(router)
    register_tracker_handlers(router)
    register_report_handlers(router)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
