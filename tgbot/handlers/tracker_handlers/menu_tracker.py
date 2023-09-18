from aiogram.types import CallbackQuery
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.buttons_names import TrackersButtons
from tgbot.utils.answer_text import options_text, launch_tracker_text, started_tracker_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_tracker_options(call: CallbackQuery, redis_client: Redis) -> None:
    user_id = call.from_user.id
    await call.message.delete()
    is_tracker = await is_redis_hexists_tracker(user_id, redis_client)
    if is_tracker:
        started_tracker = await started_tracker_text(user_id, redis_client)
        markup = await menu_inline_kb(await TrackersButtons.tracker_menu_stop())
        await call.message.answer(text=launch_tracker_text + started_tracker, reply_markup=markup)
    else:
        markup = await menu_inline_kb(await TrackersButtons.tracker_menu_start())
        await call.message.answer(text=options_text, reply_markup=markup)


async def no_btn_handler(call: CallbackQuery) -> None:
    markup = await menu_inline_kb(await TrackersButtons.tracker_menu_stop())
    await call.message.edit_text(text=options_text, reply_markup=markup)
