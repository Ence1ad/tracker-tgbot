from enum import Enum

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


class CommandName(Enum):
    START: str = 'start'
    HELP: str = 'help'
    SETTINGS: str = 'settings'
    CANCEL: str = 'cancel'


async def my_commands(bot: Bot) -> None:
    """
    The my_commands function is used to set the commands that will be shown in the bot's profile.

    :param bot: Bot: Access the bot's methods
    :return: A list of bot command objects
    """
    commands = [
        BotCommand(
            command=CommandName.START.value,
            description="Tap this button to begin using the bot"
        ),
        BotCommand(
            command=CommandName.HELP.value,
            description="Use this button to access helpful information and guidance on how to use the bot."
        ),
        BotCommand(
            command=CommandName.SETTINGS.value,
            description='Tap this button to customize your language preferences and settings within the bot.'
        ),
        BotCommand(
            command=CommandName.CANCEL.value,
            description='If you want to stop the current task or conversation, use this button'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
