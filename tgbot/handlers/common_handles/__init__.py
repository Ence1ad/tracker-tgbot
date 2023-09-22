from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import any_state

from tgbot.handlers.common_handles.cancel_handler import callback_cancel_handler
from tgbot.handlers.common_handles.settings_handler import set_user_language, set_ru_lang, set_en_lang
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.bot_commands import CommandName


def register_common_handlers() -> Router:
    from .start_handler import command_start_handler
    from .cancel_handler import command_cancel_handler
    from .exit_handler import exit_menu_handler
    from .help_handler import command_help_handler
    from .settings_handler import command_settings_handler

    router = Router()

    router.message.register(command_start_handler, Command(CommandName.START.name, ignore_case=True))
    router.message.register(command_cancel_handler, Command(CommandName.CANCEL.name, ignore_case=True), any_state)
    router.callback_query.register(callback_cancel_handler, F.data == AppButtons.general_data.CANCEL_BTN.name,
                                   any_state)
    router.callback_query.register(exit_menu_handler, F.data == AppButtons.general_data.EXIT_BTN.name)
    router.message.register(command_help_handler, Command(CommandName.HELP.name, ignore_case=True))
    router.message.register(command_settings_handler, Command(CommandName.SETTINGS.name, ignore_case=True))
    router.callback_query.register(set_user_language, F.data == AppButtons.settings_data.LANGUAGE.name)
    router.callback_query.register(set_ru_lang, (F.data == AppButtons.settings_data.RUSSIA.name)
                                   | (F.data == AppButtons.settings_data.X_RUSSIA.name))
    router.callback_query.register(set_en_lang, (F.data == AppButtons.settings_data.ENGLISH.name) |
                                   (F.data == AppButtons.settings_data.X_ENGLISH.name))
    return router
