from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start, choice_buttons
from tgbot.utils.answer_text import not_launched_tracker_text, launch_tracker_text, \
    answer_stop_tracker_text, started_tracker_text


async def select_launched_tracker(call: CallbackQuery, redis_client: Redis) -> Message:
    user_id = call.from_user.id
    is_tracker = await is_redis_hexists_tracker(user_id, redis_client)
    if is_tracker:
        started_tracker = await started_tracker_text(user_id, redis_client)
        await call.message.delete()
        markup = await menu_inline_kb(choice_buttons)
        return await call.message.answer(text=launch_tracker_text + started_tracker + answer_stop_tracker_text,
                                         reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        return await call.message.answer(text=not_launched_tracker_text, reply_markup=markup)
