from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def my_commands(bot: Bot) -> None:
    commands = [
        BotCommand(
            command='start',
            description='Start bot'
        ),
        BotCommand(
            command='help',
            description='Get help'
        ),
        BotCommand(
            command='settings',
            description='Set bot parameters'
        ),
        BotCommand(
            command='cancel',
            description='Cancellation of the action'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
