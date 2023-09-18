from aiogram.types import CallbackQuery

from tgbot.keyboards.buttons_names import ReportsButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import options_text


async def get_report_options(call: CallbackQuery) -> None:
    markup = await menu_inline_kb(await ReportsButtons.report_menu())
    await call.message.edit_text(text=options_text,  reply_markup=markup)
