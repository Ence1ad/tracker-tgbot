from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def my_commands(bot: Bot) -> None:
    commands = [
        BotCommand(
            command='start',
            description='Start work'
        ),
        BotCommand(
            command='help',
            description='Get help'
        ),
        BotCommand(
            command='settings',
            description='Adjust bot'
        ),
        BotCommand(
            command='cancel',
            description='Canceling'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
