from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import any_state


def register_common_handlers() -> Router:
    """

    The register_common_handlers function is a router that handles all the common related callbacks.
    It registers handlers for:
        - displaying the main menu of the bot;
        - canceling user's state;
        - getting description of the bot operation;
        - getting user settings;

    :return: A router object

    """
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.utils.bot_commands import CommandName
    from .start_handler import command_start_handler
    from .cancel_handler import command_cancel_handler, callback_cancel_handler
    from .exit_handler import exit_menu_handler
    from .help_handler import command_help_handler
    from .settings_handler import command_settings_handler, language_settings, set_user_lang

    router = Router()

    router.message.register(command_start_handler, Command(CommandName.START.name, ignore_case=True))
    router.message.register(command_cancel_handler, Command(CommandName.CANCEL.name, ignore_case=True), any_state)
    router.callback_query.register(callback_cancel_handler, F.data == AppButtons.general_data.CANCEL_BTN.name,
                                   any_state)
    router.callback_query.register(exit_menu_handler, F.data == AppButtons.general_data.EXIT_BTN.name)
    router.message.register(command_help_handler, Command(CommandName.HELP.name, ignore_case=True))
    router.message.register(command_settings_handler, Command(CommandName.SETTINGS.name, ignore_case=True))
    router.callback_query.register(language_settings, F.data == AppButtons.settings_data.LANGUAGE.name)
    router.callback_query.register(set_user_lang, (F.data == AppButtons.settings_data.RUSSIA.name)
                                   | (F.data == AppButtons.settings_data.X_RUSSIA.name))
    router.callback_query.register(set_user_lang, (F.data == AppButtons.settings_data.ENGLISH.name) |
                                   (F.data == AppButtons.settings_data.X_ENGLISH.name))
    return router
