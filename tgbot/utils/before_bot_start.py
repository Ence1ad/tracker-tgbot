from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, BotName, Message

from config import settings
from tgbot.utils.bot_commands import bot_commands


async def start_bot(bot: Bot) -> Message:
    """Start the bot and send a notification to the admin.

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


async def is_bot_admin(bot: Bot, chat_id: int) -> None:
    """Check if the bot is an administrator in the specified chat.

    This function checks whether the bot is an administrator in the given chat. If not,
    it raises a PermissionError indicating that the bot does not have the required
    administrator status.

    :param bot: The Bot instance representing the bot.
    :param chat_id: The ID of the chat to check.
    :raises PermissionError: If the bot is not an administrator in the specified chat.
    """
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
    if not isinstance(chat_member, ChatMemberAdministrator):
        raise PermissionError("Bot is not an administrator")
