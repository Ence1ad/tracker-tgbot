from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def main_menu_reports_handler(call: CallbackQuery, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The main_menu_reports_handler function will edit the message that triggered it to display a new
    inline keyboard with options for reporting.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: The message text and the inline keyboard with main menu reports buttons
    """
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.report_menu(), i18n)
    return await call.message.edit_text(text=i18n.get('options_text'),  reply_markup=markup)
