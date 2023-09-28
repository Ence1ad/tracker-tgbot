from aiogram.types import Message
from redis.asyncio import Redis

from cache.redis_language_commands import redis_hget_lang
from config import settings
from tgbot.utils.jinja_engine import render_template


async def command_help_handler(message: Message, redis_client: Redis) -> Message:
    """
    The command_help_handler function is a handler for the /help command.
    The function responds to the user with the help_handler_text string.

    :param message: Message: Get the message object that was sent by the user
    :param redis_client: Redis: Get the redis client from the middleware
    :return: The text of the help
    """
    user_id: int = message.from_user.id
    local: str = await redis_hget_lang(user_id=user_id, redis_client=redis_client)
    if local == settings.RU_LANG_CODE:
        help_handler_text: str = render_template('ru_help_handler.html')
    else:
        help_handler_text: str = render_template('en_help_handler.html')
    return await message.answer(text=help_handler_text)
