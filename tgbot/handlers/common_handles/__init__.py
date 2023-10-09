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
    from .start_handler import command_start_handler

    router = Router()
    router.message.register(command_start_handler, Command('start', ignore_case=True))

    return router