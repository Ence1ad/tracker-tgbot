from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_launch_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons
from tgbot.keyboards.inline_kb import stop_tracker_inline_kb
from tgbot.utils.answer_text import traker_text, not_launched_tracker_text, launch_tracker_text, \
    answer_stop_tracker_text


async def select_launched_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    tracker = await get_launch_tracker(user_id)

    if tracker:
        track_text = await traker_text(call, tracker)
        markup = await stop_tracker_inline_kb()
        await call.message.answer(text=launch_tracker_text + track_text + answer_stop_tracker_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons)
        await call.message.answer(text=not_launched_tracker_text, reply_markup=markup)
