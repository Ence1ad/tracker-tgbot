from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_launch_tracker
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start, tracker_menu_buttons_stop
from tgbot.utils.answer_text import options_text, traker_text, launch_tracker_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_tracker_options(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    tracker = await get_launch_tracker(user_id)
    if tracker:
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        track_text = await traker_text(call, tracker)
        await call.message.edit_text(text=launch_tracker_text + track_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.answer(text=options_text, reply_markup=markup)


async def no_btn_handler(call: CallbackQuery):
    # await call.message.delete()
    markup = await menu_inline_kb(tracker_menu_buttons_stop)
    await call.message.edit_text(text=options_text, reply_markup=markup)
