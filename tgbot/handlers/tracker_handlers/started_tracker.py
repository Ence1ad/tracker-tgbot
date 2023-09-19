from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import not_launched_tracker_text, answer_stop_tracker_text, started_tracker_text


async def select_launched_tracker(call: CallbackQuery, redis_client: Redis, buttons: AppButtons) -> Message:
    user_id = call.from_user.id
    is_tracker = await is_redis_hexists_tracker(user_id, redis_client)
    if is_tracker:
        started_tracker = await started_tracker_text(user_id, redis_client)
        await call.message.delete()
        markup = await menu_inline_kb(await buttons.yes_no_menu())
        return await call.message.answer(text=started_tracker + answer_stop_tracker_text,
                                         reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(await buttons.tracker_menu_start())
        return await call.message.answer(text=not_launched_tracker_text, reply_markup=markup)
