from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from tgbot.utils.answer_text import canceling_text, exit_text


async def command_cancel_handler(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if isinstance(event, Message):
        await event.delete()
        await event.answer(text=canceling_text)
    elif isinstance(event, CallbackQuery):
        await event.answer(text=exit_text)
        await event.message.delete()
