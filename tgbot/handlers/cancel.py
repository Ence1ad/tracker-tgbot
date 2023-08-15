from aiogram.types import CallbackQuery


async def command_cancel_handler(call: CallbackQuery):
    await call.message.delete()
