from datetime import datetime

from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import update_tracker, get_launch_tracker
from db.tracker.tracker_model import Tracker
from tgbot.utils.answer_text import traker_text, stop_tracker_text, not_launched_tracker_text


async def stop_tracker_handler(call: CallbackQuery):
    user_id: int = call.from_user.id
    call_datetime: datetime = call.message.date
    await call.message.delete()
    tracker: Tracker = await get_launch_tracker(user_id)
    if tracker:
        tracker_id = tracker.Tracker.tracker_id
        await update_tracker(user_id=user_id, call_datetime=call_datetime, tracker_id=tracker_id)
        track_text = await traker_text(call, tracker)
        await call.message.answer(text=stop_tracker_text + track_text)
    else:
        await call.message.answer(text=not_launched_tracker_text)
