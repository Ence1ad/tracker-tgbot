from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from data_preparation.pd_prepare import pd_data
from db.report.report_commands import get_report
from tgbot.keyboards.buttons_names import reports_buttons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import xlsx_title, send_report_text, empty_trackers_text
from data_preparation.create_report import create_bar


async def get_weekly_report(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession]) -> Message:
    user_id = call.from_user.id
    report = await get_report(user_id, db_session)
    markup = await menu_inline_kb(reports_buttons)
    if report:
        data = await pd_data(report)
        await create_bar(rows=data, max_col=len(data)+1)
        await call.answer(text=send_report_text)
        await call.message.delete()
        document = FSInputFile(xlsx_title)
        return await call.bot.send_document(chat_id=call.from_user.id, document=document)
    else:
        return await call.message.edit_text(text=empty_trackers_text, reply_markup=markup)
