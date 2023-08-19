from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_user_tracker, get_launch_tracker
from tgbot.keyboards.buttons_names import reports_buttons, tracker_two_buttons, choice_buttons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import options_text, empty_tracker_text, traker_text, just_one_tracker


async def get_report_options(call: CallbackQuery):
    # TODO переделать функцию, сделать ее более умной
    user_id = call.from_user.id
    await call.message.delete()
    if await get_user_tracker(user_id):
        markup = await menu_inline_kb(reports_buttons)
        await call.message.answer(text=options_text,  reply_markup=markup)
    else:
        if tracker := await get_launch_tracker(user_id):
            markup = await menu_inline_kb(choice_buttons)
            track_text = await traker_text(call, tracker)
            await call.message.answer(text=just_one_tracker + track_text, reply_markup=markup)
        else:
            markup = await menu_inline_kb(tracker_two_buttons)
            await call.message.answer(text=empty_tracker_text, reply_markup=markup)
