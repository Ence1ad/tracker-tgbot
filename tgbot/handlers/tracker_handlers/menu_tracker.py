from aiogram.types import CallbackQuery

from tgbot.keyboards.buttons_names import tracker_menu_buttons
from tgbot.utils.answer_text import options_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_tracker_options(call: CallbackQuery):
    await call.message.delete()
    markup = await menu_inline_kb(tracker_menu_buttons)
    await call.message.answer(text=options_text, reply_markup=markup)


async def no_btn_handler(call: CallbackQuery):
    await call.message.delete()
    markup = await menu_inline_kb(tracker_menu_buttons)
    await call.message.answer(text=options_text, reply_markup=markup)
