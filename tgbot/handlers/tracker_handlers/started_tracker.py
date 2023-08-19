from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_launch_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start, choice_buttons
from tgbot.utils.answer_text import traker_text, not_launched_tracker_text, launch_tracker_text, \
    answer_stop_tracker_text


async def select_launched_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    started_tracker = await get_launch_tracker(user_id)
    if started_tracker:
        track_text = await traker_text(call, started_tracker)
        markup = await menu_inline_kb(choice_buttons)
        await call.message.answer(text=launch_tracker_text + track_text + answer_stop_tracker_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.answer(text=not_launched_tracker_text, reply_markup=markup)
