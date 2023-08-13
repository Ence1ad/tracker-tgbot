from aiogram.types import CallbackQuery


async def del_tracking_data(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(text="Not implemented")
