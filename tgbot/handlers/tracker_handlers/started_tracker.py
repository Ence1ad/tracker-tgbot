from aiogram.types import CallbackQuery
from redis.asyncio import Redis

from cache.redis_commands import redis_started_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start, choice_buttons
from tgbot.utils.answer_text import not_launched_tracker_text, launch_tracker_text, \
    answer_stop_tracker_text


async def select_launched_tracker(call: CallbackQuery, redis_client: Redis):
    user_id = call.from_user.id
    started_tracker = await redis_started_tracker(user_id, redis_client)
    if started_tracker:
        await call.message.delete()
        markup = await menu_inline_kb(choice_buttons)
        await call.message.answer(text=launch_tracker_text + started_tracker + answer_stop_tracker_text,
                                  reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.answer(text=not_launched_tracker_text, reply_markup=markup)
