from aiogram.types import CallbackQuery

from tgbot.handlers.actions_handlers.show_actions import USER_CATEGORY
from tgbot.utils.answer_text import new_tracker_text
from tgbot.keyboards.callback_data_classes import SelectActionTrackerCallback

from db.tracker.tracker_db_command import create_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons


# TODO трекер должен автоматом останавливаться через нужное время
async def create_new_tracker(call: CallbackQuery, callback_data: SelectActionTrackerCallback):
    user_id = call.from_user.id
    start_time = call.message.date
    action_id = callback_data.action_id
    action_name = callback_data.action_name
    await call.message.delete()
    await create_tracker(user_id, category_id=USER_CATEGORY[user_id], action_id=action_id,
                         track_start=start_time)
    markup = await menu_inline_kb(tracker_menu_buttons)
    await call.message.answer(text=f"{new_tracker_text} {action_name}", reply_markup=markup)
