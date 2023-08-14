from aiogram.types import CallbackQuery

from tgbot.keyboards.buttons_names import start_menu_buttons
from tgbot.keyboards.menu_kb import menu_inline_kb
from tgbot.utils.answer_text import options_text


async def exit_menu(call: CallbackQuery):
    markup = await menu_inline_kb(start_menu_buttons)
    await call.message.delete()
    await call.message.answer(text=options_text, reply_markup=markup)
