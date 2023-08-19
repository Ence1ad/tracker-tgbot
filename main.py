import asyncio
import logging

from aiogram.filters import Command
from aiogram import Dispatcher, Router, F
from aiogram.fsm.state import any_state

from config import bot
from tgbot.handlers import register_categories_handlers, register_actions_handlers, register_tracker_handlers,\
     register_report_handlers
from tgbot.handlers.cancel import command_cancel_handler
from tgbot.handlers.exit_handler import exit_menu
from tgbot.handlers.help_handler import command_help_handler
from tgbot.handlers.settings_handler import command_settings_handler

from tgbot.handlers.start import command_start_handler
from tgbot.keyboards.buttons_names import exit_btn, cancel_btn
from tgbot.utils.bot_commands import my_commands
from aiogram.fsm.storage.redis import RedisStorage
router = Router()


async def start_bot(tgbot):
    await my_commands(tgbot)


async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher(storage=RedisStorage.from_url("redis://localhost:6379/0"))
    await start_bot(bot)
    dp.include_router(router)
    router.message.register(command_start_handler, Command("start"))
    router.message.register(command_cancel_handler, Command(commands=["cancel"]), any_state)
    router.callback_query.register(command_cancel_handler, F.data == cancel_btn, any_state)
    router.callback_query.register(exit_menu, F.data == exit_btn)
    router.message.register(command_help_handler, Command(commands=["help"]))
    router.message.register(command_settings_handler, Command(commands=["settings"]))
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
