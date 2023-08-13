import asyncio

from aiogram.types import CallbackQuery, FSInputFile

from config import bot
from db.report.report_commands import get_report
from tgbot.handlers.reports_handlers.create_report import create_bar
from tgbot.utils.prepare_data import adjust_data_main, _get_headers


async def get_report_options(call: CallbackQuery):
    user_id = call.from_user.id
    # TODO сделать чтобы нельзя было создать отчет пока запущена активность
    report = await get_report(user_id)
    report = list(report)
    if report:
        max_row = await _get_headers(report)
        max_row = len(max_row)+1
        data_for_bar = await adjust_data_main(report)
        await asyncio.create_task(create_bar(rows=data_for_bar, max_col=max_row))

        await call.message.delete()
        await call.message.answer(text="This is your report")
        document = FSInputFile('bar.xlsx')
        return await bot.send_document(chat_id=call.from_user.id, document=document)
    else:
        return await call.message.answer(text="You don't have any trackers")

