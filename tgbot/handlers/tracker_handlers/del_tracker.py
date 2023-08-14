from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_user_tracker, delete_tracker
from tgbot.keyboards.tracker_kb import list_trackers_inline_kb
from tgbot.utils.answer_text import daily_tracker_text, empty_tracker_text, delete_tracker_text
from tgbot.utils.callback_data_classes import DeleteTrackerCallback


async def select_removing_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    tracker = await get_user_tracker(user_id)
    tracker = list(tracker)
    if tracker:
        await call.message.delete()
        markup = await list_trackers_inline_kb(tracker, callback_class=DeleteTrackerCallback)
        await call.message.answer(text=daily_tracker_text, reply_markup=markup)
    else:
        await call.message.delete()
        await call.message.answer(text=empty_tracker_text)


async def del_tracking_data(call: CallbackQuery, callback_data: DeleteTrackerCallback):
    user_id = call.from_user.id
    tracker_id = callback_data.tracker_id
    await delete_tracker(user_id=user_id, tracker_id=tracker_id)
    await call.message.delete()
    await call.message.answer(text=delete_tracker_text)
