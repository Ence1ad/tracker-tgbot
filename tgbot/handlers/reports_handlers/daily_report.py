from aiogram.types import CallbackQuery


# TODO отчет должен выводить месячные данные
async def report_monthly_tracking(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(text="Not implemented")
