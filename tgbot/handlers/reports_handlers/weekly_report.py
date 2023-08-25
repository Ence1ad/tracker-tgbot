from aiogram.types import CallbackQuery, FSInputFile

from config import bot
from data_preparation.pd_prepare import pd_data
from db.report.report_commands import get_report
from tgbot.keyboards.buttons_names import reports_buttons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import xlsx_title, send_report_text, empty_trackers_text
from data_preparation.create_report import create_bar
# from data_preparation.prepare_data import adjust_data_main, get_headers


async def get_weekly_report(call: CallbackQuery):
    user_id = call.from_user.id
    report = await get_report(user_id)
    report = list(report)
    markup = await menu_inline_kb(reports_buttons)
    if report:
        # max_row = await get_headers(report)
        # max_row = len(max_row)+1
        # data_for_bar = await adjust_data_main(report)
        # await create_bar(rows=data_for_bar, max_col=max_row)
        data = await pd_data(report)
        await create_bar(rows=data, max_col=len(data))
        await call.answer(text=send_report_text)
        await call.message.delete()
        document = FSInputFile(xlsx_title)
        return await bot.send_document(chat_id=call.from_user.id, document=document)
    else:
        return await call.message.edit_text(text=empty_trackers_text, reply_markup=markup)
