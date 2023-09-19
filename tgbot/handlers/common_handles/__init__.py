from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import any_state

from tgbot.keyboards.app_buttons import AppButtons


def register_common_handlers() -> Router:
    from .start_handler import command_start_handler
    from .cancel_handler import command_cancel_handler
    from .exit_handler import exit_menu_handler
    from .help_handler import command_help_handler
    from .settings_handler import command_settings_handler

    router = Router()

    router.message.register(command_start_handler, Command("start"))
    router.message.register(command_cancel_handler, Command(commands=["cancel"]), any_state)
    router.callback_query.register(command_cancel_handler, F.data == AppButtons.general_data.CANCEL_BTN.name, any_state)
    router.callback_query.register(exit_menu_handler, F.data == AppButtons.general_data.EXIT_BTN.name)
    router.message.register(command_help_handler, Command(commands=["help"]))
    router.message.register(command_settings_handler, Command(commands=["settings"]))
    return router
