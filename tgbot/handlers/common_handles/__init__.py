from aiogram import Router, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, JOIN_TRANSITION,\
    LEAVE_TRANSITION

from config import settings


def register_common_handlers() -> Router:
    """Register common message and callback handlers for your Telegram bot.

    This function sets up various handlers for your bot to handle messages and events,
     including:
    - Starting the bot.
    - Cancelling the current action.
    - Exiting from a menu.
    - Providing help.
    - Managing user settings.
    - Adding and removing users from the group.
    - Handling language settings.

    :return: A configured Router object with the registered handlers.
    """
    from .start_handler import command_start_handler
    from .user_group_status import add_user_handler, remove_user_handler

    router = Router()
    router.message.filter(F.chat.id == F.from_user.id)
    router.chat_member.filter(F.chat.id == settings.GROUP_ID)
    router.chat_member.register(
        add_user_handler,
        ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION)
    )
    router.chat_member.register(
        remove_user_handler,
        ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION)
    )

    router.message.register(command_start_handler, Command('start', ignore_case=True))

    return router
