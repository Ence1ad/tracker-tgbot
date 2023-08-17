from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_launch_tracker
from tgbot.keyboards.buttons_names import tracker_menu_buttons
from tgbot.utils.answer_text import options_text, traker_text, launch_tracker_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_tracker_options(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    markup = await menu_inline_kb(tracker_menu_buttons)
    tracker = await get_launch_tracker(user_id)
    if tracker:
        track_text = await traker_text(call, tracker)
        await call.message.answer(text=launch_tracker_text + track_text, reply_markup=markup)
    else:
        await call.message.answer(text=options_text, reply_markup=markup)


async def no_btn_handler(call: CallbackQuery):
    await call.message.delete()
    markup = await menu_inline_kb(tracker_menu_buttons)
    await call.message.answer(text=options_text, reply_markup=markup)
