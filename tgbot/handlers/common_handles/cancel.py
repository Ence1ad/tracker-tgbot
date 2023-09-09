from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext


async def command_cancel_handler(event, state: FSMContext):
    await state.clear()
    if isinstance(event, Message):
        await event.delete()
        await event.answer(text="Cancelled")
    elif isinstance(event, CallbackQuery):
        await event.answer(text="See you soon!")
        await event.message.delete()
