from datetime import datetime

from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import update_tracker, get_launch_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_stop, tracker_menu_buttons_start
from tgbot.utils.answer_text import traker_text, stop_tracker_text, not_launched_tracker_text


async def stop_tracker_handler(call: CallbackQuery):
    user_id: int = call.from_user.id
    call_datetime: datetime = call.message.date
    await call.message.delete()
    tracker = await get_launch_tracker(user_id)
    if tracker:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        tracker_id = tracker[0].tracker_id
        await update_tracker(user_id=user_id, call_datetime=call_datetime, tracker_id=tracker_id)
        track_text = await traker_text(call, tracker)
        await call.message.answer(text=stop_tracker_text + track_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        await call.message.edit_text(text=not_launched_tracker_text, reply_markup=markup)
