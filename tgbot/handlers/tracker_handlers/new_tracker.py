from datetime import datetime

from aiogram.types import CallbackQuery

from .actions_tracker import USER_TRACKER_CATEGORY
from tgbot.utils.answer_text import new_tracker_text
from tgbot.utils.callback_data_classes import SelectActionTrackerCallback

from db.tracker.tracker_db_command import create_tracker


async def create_new_tracker(call: CallbackQuery, callback_data: SelectActionTrackerCallback):
    user_id = call.from_user.id
    start_time = call.message.date
    # print(start_time.timestamp())
    # print(datetime(start_time.strftime("%Y-%m-%d %H:%M:%S")))
    action_id = callback_data.action_id
    action_name = callback_data.action_name
    await call.message.delete()
    await create_tracker(user_id, category_id=USER_TRACKER_CATEGORY[user_id], action_id=action_id,
                         track_start=start_time)
    await call.message.answer(text=f"{new_tracker_text} {action_name}")
