from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_commands import redis_started_tracker
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start, tracker_menu_buttons_stop
from tgbot.utils.answer_text import options_text, launch_tracker_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_tracker_options(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    started_tracker = await redis_started_tracker(user_id)
    if started_tracker:
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        await call.message.answer(text=launch_tracker_text + started_tracker, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.answer(text=options_text, reply_markup=markup)


async def no_btn_handler(call: CallbackQuery):
    markup = await menu_inline_kb(tracker_menu_buttons_stop)
    await call.message.edit_text(text=options_text, reply_markup=markup)
