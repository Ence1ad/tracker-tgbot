from aiogram.types import CallbackQuery

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import options_text


async def get_report_options(call: CallbackQuery, buttons: AppButtons) -> None:
    markup = await menu_inline_kb(await buttons.report_menu())
    await call.message.edit_text(text=options_text,  reply_markup=markup)
