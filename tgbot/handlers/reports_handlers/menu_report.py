from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_user_tracker
from tgbot.keyboards.buttons_names import reports_buttons
from tgbot.keyboards.menu_kb import menu_inline_kb
from tgbot.utils.answer_text import options_text, empty_tracker_text


async def get_report_options(call: CallbackQuery):
    user_id = call.from_user.id
    trackers = await get_user_tracker(user_id)
    print(trackers)
    await call.message.delete()
    if trackers:
        markup = await menu_inline_kb(reports_buttons)
        await call.message.answer(text=options_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(new_tracker_btn='⏲ Start tracking'),)
        await call.message.answer(text=empty_tracker_text, reply_markup=markup)


