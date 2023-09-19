from aiogram.types import Message

from tgbot.utils.jinja_engine import render_template


async def command_help_handler(message: Message) -> Message:
    d = {"a": 1}
    text = render_template('help_handler.html', values=d)
    return await message.answer(text=text)

