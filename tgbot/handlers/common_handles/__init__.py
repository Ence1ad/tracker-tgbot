from aiogram import Router, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram.fsm.state import any_state

from config import settings


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
    from .user_group_status import add_user_handler, remove_user_handler

    router = Router()
    router.message.filter(F.chat.id == F.from_user.id)
    router.chat_member.filter(F.chat.id == settings.GROUP_ID)
    router.chat_member.register(add_user_handler, ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
    router.chat_member.register(remove_user_handler, ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
    router.message.register(command_start_handler, Command(CommandName.START.name, ignore_case=True))
    router.message.register(command_cancel_handler, Command(CommandName.CANCEL.name, ignore_case=True), any_state)
    router.callback_query.register(callback_cancel_handler, F.data == AppButtons.general_btn_source.CANCEL_BTN.name,
                                   any_state)
    router.callback_query.register(exit_menu_handler, F.data == AppButtons.general_btn_source.EXIT_BTN.name)
    router.message.register(command_help_handler, F.text.startswith('/help'))
    router.message.register(command_settings_handler, Command(CommandName.SETTINGS.name, ignore_case=True))
    router.callback_query.register(language_settings, F.data == AppButtons.settings_btn_source.LANGUAGE.name)
    router.callback_query.register(set_user_lang, (F.data.in_(AppButtons.settings_btn_list)))

    return router
