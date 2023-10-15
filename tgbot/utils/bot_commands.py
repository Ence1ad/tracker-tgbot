from enum import Enum

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from config import settings


class CommandName(Enum):
    """
    Enumeration of bot command names.

    This enumeration defines the available command names as string constants.
    """

    START: str = 'start'
    HELP: str = 'help'
    SETTINGS: str = 'settings'
    CANCEL: str = 'cancel'


async def bot_commands(bot: Bot) -> bool:
    """
    Set custom bot commands.

    This function sets custom bot commands along with their descriptions using the
    provided Bot instance.

    :param bot: The Bot instance to set custom commands for.
    :return: bool:
    """
    commands = [
        BotCommand(
            command=CommandName.START.value,
            description="Start using the bot."
        ),

        BotCommand(
            command=CommandName.HELP.value,
            description="Access helpful information and guidance."
        ),

        BotCommand(
            command=CommandName.SETTINGS.value,
            description='Customize language preferences and settings.'
        ),

        BotCommand(
            command=CommandName.CANCEL.value,
            description='Stop the current task or conversation.'
        ),
    ]

    return await bot.set_my_commands(commands=commands,
                                     scope=BotCommandScopeAllPrivateChats(),
                                     language_code=settings.GLOBAL_LANG_CODE)
