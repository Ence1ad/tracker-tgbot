from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import options_text, started_tracker_text


async def exit_menu_handler(call: CallbackQuery, state: FSMContext, redis_client: Redis, buttons: AppButtons) -> Message:
    user_id = call.from_user.id
    markup = await start_menu_inline_kb(await buttons.main_menu_buttons())
    await state.clear()
    if await is_redis_hexists_tracker(user_id, redis_client):
        text = await started_tracker_text(user_id=user_id, redis_client=redis_client)
        return await call.message.edit_text(text=text, reply_markup=markup)
    else:
        return await call.message.edit_text(text=options_text, reply_markup=markup)
