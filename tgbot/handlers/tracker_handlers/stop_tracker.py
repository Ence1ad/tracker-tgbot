from datetime import datetime

from aiogram.types import CallbackQuery

from cache.redis_cache import redis_client
from db.tracker.tracker_db_command import update_tracker, select_started_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_stop, tracker_menu_buttons_start
from tgbot.utils.answer_text import tracker_text, stop_tracker_text, not_launched_tracker_text


async def stop_tracker_handler(call: CallbackQuery):
    user_id: int = call.from_user.id
    call_datetime: datetime = call.message.date
    tracker = await select_started_tracker(user_id)
    await call.message.delete()
    if tracker:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        tracker_id = tracker[0].tracker_id
        await update_tracker(user_id=user_id, call_datetime=call_datetime, tracker_id=tracker_id)
        track_text = await tracker_text(user_id)
        # delete tracker from redis db
        await redis_client.delete(f"{user_id}_tracker")
        await call.message.answer(text=stop_tracker_text + track_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        await call.message.edit_text(text=not_launched_tracker_text, reply_markup=markup)
