from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_user_tracker, delete_tracker
from tgbot.keyboards.buttons_names import tracker_menu_buttons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import daily_tracker_text, empty_tracker_text, delete_tracker_text
from tgbot.keyboards.callback_factories import TrackerOperation, TrackerCD


async def select_removing_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    tracker = await get_user_tracker(user_id)
    tracker = list(tracker)
    if tracker:
        await call.message.delete()
        markup = await callback_factories_kb(tracker, enum_val=TrackerOperation.DEL)
        await call.message.answer(text=daily_tracker_text, reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(tracker_menu_buttons)
        await call.message.answer(text=empty_tracker_text, reply_markup=markup)


async def del_tracking_data(call: CallbackQuery, callback_data: TrackerCD):
    user_id = call.from_user.id
    tracker_id = callback_data.tracker_id
    await delete_tracker(user_id=user_id, tracker_id=tracker_id)
    await call.message.delete()
    markup = await menu_inline_kb(tracker_menu_buttons)
    await call.message.answer(text=delete_tracker_text, reply_markup=markup)
