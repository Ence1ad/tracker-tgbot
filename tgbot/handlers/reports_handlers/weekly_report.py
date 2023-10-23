from pathlib import Path

from aiogram.types import CallbackQuery, FSInputFile, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from pandas import DataFrame
from redis.asyncio import Redis
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd, \
    redis_get_report_need_upd, redis_expireat_end_of_week
from config import settings
from db.operations.report_operations import select_weekly_trackers
from report_baker.create_report import create_fig
from report_baker.pd_prepare import pd_action_data, pd_category_data
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_weekly_report(
        call: CallbackQuery, db_session: AsyncSession, buttons: AppButtons,
        i18n: TranslatorRunner, redis_client: Redis
) -> Message:
    """Generate and send the user's weekly report.

    This function generates a user's weekly report, sends it as a document, and handles
     report updates.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param db_session: AsyncSession: The SQLAlchemy database session for database
     operations.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :param redis_client: Redis: The Redis client for caching and tracking updates.
    :return: Message: The message containing the generated report document to be sent to
     the user.
    """
    user_id: int = call.from_user.id
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.general_btn_source.main_menu_buttons(), i18n)
    document = await get_document(user_id=user_id, redis_client=redis_client,
                                  db_session=db_session)
    if document:
        await call.message.delete()
        return await call.bot.send_document(caption=i18n.get('send_report_text'),
                                            chat_id=call.from_user.id,
                                            document=document)
    else:
        return await call.message.edit_text(text=i18n.get('empty_trackers_text'),
                                            reply_markup=markup)


async def get_document(user_id, redis_client: Redis, db_session) -> FSInputFile | None:
    """Retrieve the user's weekly report document.

    This function retrieves the user's weekly report document from the file system or
    generates a new one if needed.

    :param user_id: The user's ID.
    :param redis_client: Redis: The Redis client for caching and tracking updates.
    :param db_session: The SQLAlchemy database session for database operations.
    :return: FSInputFile | None: The user's report document as a file or None if no
     document is available.
    """
    file_name = f"{settings.USER_REPORT_DIR}{user_id}/{settings.WEEKLY_XLSX_FILE_NAME}"
    is_report_need_update = await redis_get_report_need_upd(user_id, redis_client)

    if (is_report_need_update is None) or int(is_report_need_update) == 1:
        await redis_expireat_end_of_week(user_id, redis_client)
        await redis_set_report_need_upd(user_id, redis_client, value=0)
        return await create_document(user_id, db_session=db_session,
                                     file_name=file_name)
    else:
        # Get already exist report
        if Path.is_file(Path(file_name)):
            document: FSInputFile = FSInputFile(file_name)
            return document
        else:
            return await create_document(user_id, db_session=db_session,
                                         file_name=file_name)


async def create_document(user_id, db_session, file_name) -> FSInputFile | None:
    """Create the user's weekly report document.

    This function generates and creates the user's weekly report document.

    :param user_id: The user's ID.
    :param db_session: The SQLAlchemy database session for database operations.
    :param file_name: The name of the report file.
    :return: FSInputFile | None: The generated report document as a file or None if no
    report is available.
    """
    report: Sequence = await select_weekly_trackers(user_id, db_session)
    if report:
        action_data: DataFrame = await pd_action_data(report)
        category_data: DataFrame = await pd_category_data(report)
        await create_fig(df_action=action_data, df_categories=category_data,
                         file_name=file_name)
        document: FSInputFile = FSInputFile(file_name)
        return document
    else:
        return
