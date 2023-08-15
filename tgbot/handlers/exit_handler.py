from aiogram.types import CallbackQuery

from tgbot.keyboards.buttons_names import start_menu_buttons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import options_text


async def exit_menu(call: CallbackQuery):
    await call.message.delete()
    markup = await start_menu_inline_kb(start_menu_buttons)
    await call.message.answer(text=options_text, reply_markup=markup)
