from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def main_menu_reports_handler(call: CallbackQuery, buttons: AppButtons,
                                    i18n: TranslatorRunner) -> Message:
    """Handle the main menu for reports.

    This function handles the user's interaction with the main menu for reports.
    It displays available report options to the user and provides an appropriate
    response based on the user's selection.


    :param call: CallbackQuery: The CallbackQuery object representing the user's
     interaction.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Message: The message to be sent to the user as a response.
    """
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.reports_btn_source.report_menu(), i18n)
    return await call.message.edit_text(text=i18n.get('options_text'),
                                        reply_markup=markup)
