from enum import Enum

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


class CommandName(Enum):
    START: str = 'start'
    HELP: str = 'help'
    SETTINGS: str = 'settings'
    CANCEL: str = 'cancel'


async def my_commands(bot: Bot) -> None:
    commands = [
        BotCommand(
            command=CommandName.START.value,
            description='Start bot'
        ),
        BotCommand(
            command=CommandName.HELP.value,
            description='Get help'
        ),
        BotCommand(
            command=CommandName.SETTINGS.value,
            description='Set bot parameters'
        ),
        BotCommand(
            command=CommandName.CANCEL.value,
            description='Cancellation of the action'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


