from aiogram.types import Message
from redis.asyncio import Redis

from cache.redis_language_commands import redis_hget_lang
from config import settings
from tgbot.utils.jinja_engine import render_template


async def command_help_handler(message: Message, redis_client: Redis) -> Message:
    """
    Handle the /help command.

    :param message: Message: Get the message object that was sent by the user
    :param redis_client: Redis: Get the redis client from the middleware
    :return: The text of the help
    """

    # # Get the text of the user's message
    # text = message.text
    #
    # # Split the message text into words
    # words = text.split()
    #
    # # If there is only one word (i.e., just "/help" without specifying a command)
    # if len(words) == 1:
    #     # Provide a general help message
    #     await message.reply(
    #         "Welcome to the Telegram Tracker Bot! Use '/help <command>' to get help for specific commands.")
    # elif len(words) == 2:
    #     # Extract the <command> part from the message
    #     command = words[1]
    #
    #     # Provide help information based on the specific <command> requested
    #     if command == "start":
    #         await message.reply("To start using the bot, simply send '/start' in a private chat.")
    #     elif command == "Categories":
    #         await message.reply(
    #             "Use '/help Categories' to learn how to manage categories (create, delete, update, display).")
    #     elif command == "Actions":
    #         await message.reply("Explore '/help Actions' to create and manage activities within your categories.")
    #     elif command == "Trackers":
    #         await message.reply(
    #             "In the 'Trackers' menu, you can start, stop, view duration, or delete trackers for your activities and categories.")
    #     elif command == "Reports":
    #         await message.reply(
    #             "Generate weekly reports of your tracked activities with '/help Reports'. The reports are exported as Excel spreadsheets.")
    #     elif command == "Language":
    #         await message.reply(
    #             "Change the language of the application using '/help Language'. We support multiple languages!")
    #     else:
    #         await message.reply("Sorry, I don't recognize that command. Please use '/help' to see available commands.")
    # else:
    #     # Handle cases where the user entered an invalid command format
    #     await message.reply("Invalid command format. Use '/help <command>' to get help for specific commands.",
    #                         )

    user_id: int = message.from_user.id
    local: str = await redis_hget_lang(user_id=user_id, redis_client=redis_client)
    if local == settings.RU_LANG_CODE:
        help_handler_text: str = render_template('ru_help_handler.html')
    else:
        help_handler_text: str = render_template('en_help_handler.html')
    return await message.answer(text=help_handler_text)
