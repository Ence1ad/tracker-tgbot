from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, BotName, Message

from config import settings
from tgbot.utils.bot_commands import bot_commands


async def start_bot(bot: Bot) -> Message:
    """
    Start the bot and send a notification to the admin.

    This function initializes the bot by getting its commands and sending
    a notification to the admin to indicate that the bot has been launched.

    :param bot: The Bot instance representing the bot.
    :return: Message
    """
    # Get commands
    await bot_commands(bot)
    bot_name: BotName = await bot.get_my_name()
    return await bot.send_message(chat_id=settings.ADMIN_ID,
                                  text=f'The "{bot_name}" bot has been launched!')

