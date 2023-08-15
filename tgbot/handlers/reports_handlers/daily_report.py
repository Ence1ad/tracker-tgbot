from aiogram.types import CallbackQuery


# TODO отчет должен выводить дневные данные
async def report_daily_tracking(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(text="Not implemented")
