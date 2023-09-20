from aiogram.types import Message

from tgbot.utils.jinja_engine import render_template


async def command_help_handler(message: Message) -> Message:
    """
    The command_help_handler function is a handler for the /help command.
    The function responds to the user with the help_handler_text string.

    :param message: Message: Get the message object that was sent by the user
    :return: The text of the help
    """

    if message.from_user.language_code == 'ru':
        help_handler_text = render_template('ru_help_handler.html', values={"a": 1})
    else:
        help_handler_text = render_template('en_help_handler.html', values={"a": 1})
    return await message.answer(text=help_handler_text)

