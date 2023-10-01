from aiogram.types import CallbackQuery, FSInputFile, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from pandas import DataFrame
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from data_preparation.pd_prepare import pd_action_data, pd_category_data
from db.report.report_commands import select_weekly_trackers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from data_preparation.create_report import create_fig


async def get_weekly_report(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                            buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The get_weekly_report function retrieves all trackers from a given week and creates an Excel file with two sheets:
    one for actions, and another for categories. The function then sends this file to the user.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with a report on the user's actions for the week
    """
    user_id: int = call.from_user.id
    report: list[Row] = await select_weekly_trackers(user_id, db_session)
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.general_btn_source.main_menu_buttons(), i18n)
    if report:
        action_data: DataFrame = await pd_action_data(report)
        category_data: DataFrame = await pd_category_data(report)
        await create_fig(df_action=action_data, df_categories=category_data)
        await call.message.delete()
        document: FSInputFile = FSInputFile(settings.WEEKLY_XLSX_FILE_NAME)
        return await call.bot.send_document(caption=i18n.get('send_report_text'), chat_id=call.from_user.id,
                                            document=document)
    else:
        return await call.message.edit_text(text=i18n.get('empty_trackers_text'), reply_markup=markup)
