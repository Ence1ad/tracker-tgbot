from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import any_state

from tgbot.keyboards.buttons_names import CustomButtons


def register_common_handlers() -> Router:
    from .start import command_start_handler
    from .cancel import command_cancel_handler
    from .exit_handler import exit_menu
    from .help_handler import command_help_handler
    from .settings_handler import command_settings_handler

    router = Router()

    router.message.register(command_start_handler, Command("start"))
    router.message.register(command_cancel_handler, Command(commands=["cancel"]), any_state)
    router.callback_query.register(command_cancel_handler, F.data == CustomButtons.cancel_btn, any_state)
    router.callback_query.register(exit_menu, F.data == CustomButtons.exit_btn)
    router.message.register(command_help_handler, Command(commands=["help"]))
    router.message.register(command_settings_handler, Command(commands=["settings"]))

    return router
