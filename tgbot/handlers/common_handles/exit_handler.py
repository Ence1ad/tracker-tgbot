from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from cache.redis_commands import is_redis_tracker_exist
from tgbot.keyboards.buttons_names import start_menu_buttons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import options_text, launch_tracker_text, started_tracker_text


async def exit_menu(call: CallbackQuery, state: FSMContext, redis_client: Redis) -> Message:
    user_id = call.from_user.id
    markup = await start_menu_inline_kb(start_menu_buttons)
    await state.clear()
    if await is_redis_tracker_exist(user_id, redis_client):
        started_text = await started_tracker_text(user_id, redis_client)
        return await call.message.edit_text(text=launch_tracker_text + started_text, reply_markup=markup)
    else:
        return await call.message.edit_text(text=options_text, reply_markup=markup)
