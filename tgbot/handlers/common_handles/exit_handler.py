from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.redis_commands import redis_started_tracker, is_redis_tracker_exist
from tgbot.keyboards.buttons_names import start_menu_buttons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import options_text, launch_tracker_text


async def exit_menu(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    markup = await start_menu_inline_kb(start_menu_buttons)
    await state.clear()
    if await is_redis_tracker_exist(user_id):
        started_text = await redis_started_tracker(user_id)
        await call.message.edit_text(text=launch_tracker_text + started_text, reply_markup=markup)
    else:
        await call.message.edit_text(text=options_text, reply_markup=markup)
