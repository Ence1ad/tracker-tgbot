from pathlib import Path

from aiogram.types import CallbackQuery, FSInputFile, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from pandas import DataFrame
from redis.asyncio import Redis
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.reports_redis_manager import redis_set_report_need_upd, redis_get_report_need_upd, redis_expireat_end_of_week
from config import settings
from report_baker.pd_prepare import pd_action_data, pd_category_data
from db.report.report_commands import select_weekly_trackers
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from report_baker.create_report import create_fig


async def get_weekly_report(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                            buttons: AppButtons, i18n: TranslatorRunner, redis_client: Redis) -> Message:
    """
    The get_weekly_report function retrieves all trackers from a given week and creates an Excel file with two sheets:
    one for actions, and another for categories. The function then sends this file to the user.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the redis client from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with a report on the user's actions for the week
    """
    user_id: int = call.from_user.id
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.general_btn_source.main_menu_buttons(), i18n)
    document = await get_document(user_id=user_id, redis_client=redis_client, db_session=db_session)
    if document:
        await call.message.delete()
        return await call.bot.send_document(caption=i18n.get('send_report_text'), chat_id=call.from_user.id,
                                            document=document)
    else:
        return await call.message.edit_text(text=i18n.get('empty_trackers_text'), reply_markup=markup)


async def get_document(user_id, redis_client: Redis, db_session) -> FSInputFile | None:
    """
    Get user's report document from user's folder

    :param user_id: Create a directory for the user
    :param redis_client: Redis: Get the redis client from the middleware
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :return: A document
    """
    # Create user_report dir if not exists
    await _create_user_report_dir(user_id)

    await redis_expireat_end_of_week(user_id, redis_client)
    sheet_name = f"{settings.USER_REPORT_DIR}{user_id}/{settings.WEEKLY_XLSX_FILE_NAME}"
    is_report_need_update = await redis_get_report_need_upd(user_id, redis_client)
    if is_report_need_update and int(is_report_need_update):
        await redis_set_report_need_upd(user_id, redis_client, value=0)
        return await create_document(user_id, db_session=db_session, sheet_name=sheet_name)
    else:
        # Get already exist report
        if Path.exists(Path(sheet_name)):
            document: FSInputFile = FSInputFile(sheet_name)
            return document
        else:
            return await create_document(user_id, db_session=db_session, sheet_name=sheet_name)


async def _create_user_report_dir(user_id: int) -> None:
    """
    Creates a directory for the user's reports.

    :param user_id: Create a directory for the user's reports
    :return: The path to the user report directory
    """
    user_report_dir: Path = Path(f'{settings.USER_REPORT_DIR}{user_id}')
    if not Path.exists(user_report_dir):
        Path.mkdir(user_report_dir)


async def create_document(user_id, db_session, sheet_name) -> FSInputFile | None:
    """
    Create new user report document

    :param user_id: Select the user's data from the database
    :param db_session: Create a connection to the database
    :param sheet_name: Name the document that is created
    :return: An FSInputFile object
    """
    report: list[Row] = await select_weekly_trackers(user_id, db_session)
    if report:
        action_data: DataFrame = await pd_action_data(report)
        category_data: DataFrame = await pd_category_data(report)
        await create_fig(df_action=action_data, df_categories=category_data, sheet_name=sheet_name)
        document: FSInputFile = FSInputFile(sheet_name)
        return document
    else:
        return
