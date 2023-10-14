from aiogram.types import Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.language_redis_manager import redis_hget_lang
from config import settings
from tgbot.template_engine.jinja_engine import render_template


async def command_help_handler(message: Message, redis_client: Redis, i18n: TranslatorRunner) -> Message:
    """
    Handle the /help command.

    :param message: Message: Get the message object that was sent by the user
    :param redis_client: Redis: Get the redis client from the middleware
    :return: The text of the help
    """
    user_id: int = message.from_user.id
    current_user_lang = await redis_hget_lang(user_id=user_id, redis_client=redis_client)

    if current_user_lang == settings.RU_LANG_CODE:
        lang_code: dict[str:str] = {
            "main": 'ru_help_main.html',
            "cat": 'ru_help_categories.html',
            "act": 'ru_help_actions.html',
            "tra": 'ru_help_trackers.html',
            "rep": 'ru_help_reports.html'
        }
    else:
        lang_code = {
            "main": 'en_help_main.html',
            "cat": 'en_help_categories.html',
            "act": 'en_help_actions.html',
            "tra": 'en_help_trackers.html',
            "rep": 'en_help_reports.html'
        }

    # Get the text of the user's message
    text = message.text

    # Split the message text into words
    words = text.split('_')
    # If there is only one word (i.e., just "/help" without specifying a command)
    if len(words) == 1:
        # Provide a general help message
        general_help_msg: str = render_template(lang_code.get("main"))
        return await message.reply(text=general_help_msg)
    elif len(words) == 2:
        # Extract the <command> part from the message
        command = words[1]

        if command == "cat":
            categories_help_msg: str = render_template(lang_code.get("cat"))
            return await message.reply(text=categories_help_msg)
        elif command == "act":
            actions_help_msg: str = render_template(lang_code.get("act"))
            return await message.reply(text=actions_help_msg)
        elif command == "tra":
            trackers_help_msg: str = render_template(lang_code.get("tra"))
            return await message.reply(text=trackers_help_msg)
        elif command == "rep":
            reports_help_msg: str = render_template(lang_code.get("rep"))
            return await message.reply(text=reports_help_msg)
        else:
            return await message.reply(text=i18n.get('help_unknown_command_text'))
    else:
        # Handle cases where the user entered an invalid command format
        return await message.reply(text=i18n.get('help_invalid_command_format_text'))

