from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_report_options(call: CallbackQuery, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    markup = await menu_inline_kb(await buttons.report_menu(), i18n)
    return await call.message.edit_text(text=i18n.get('options_text'),  reply_markup=markup)
