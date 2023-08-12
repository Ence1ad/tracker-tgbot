from aiogram.types import CallbackQuery

from tgbot.utils.answer_text import options_text
from tgbot.keyboards.tracker_kb import tracker_menu_inline_kb


async def get_tracker_options(call: CallbackQuery):
    await call.message.delete()
    markup = await tracker_menu_inline_kb()
    await call.message.answer(text=options_text, reply_markup=markup)


async def no_btn_handler(call: CallbackQuery):
    await call.message.delete()
    markup = await tracker_menu_inline_kb()
    await call.message.answer(text=options_text, reply_markup=markup)

