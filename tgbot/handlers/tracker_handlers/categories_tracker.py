from datetime import datetime

from aiogram.types import CallbackQuery

from db.tracker.tracker_db_command import get_launch_tracker
from db.tracker.tracker_model import Tracker
from tgbot.utils.answer_text import select_category_text, traker_text, already_launch_tracker_text
from tgbot.keyboards.categories_kb import list_categories_inline_kb
from tgbot.handlers.categories_handlers.show_categories import show_user_category
from tgbot.utils.callback_data_classes import SelectCategoryTrackerCallback


async def select_category_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    call_datetime: datetime = call.message.date
    tracker: Tracker = await get_launch_tracker(user_id)
    if not tracker:
        categories: list = list(await show_user_category(call))
        if categories:
            markup = await list_categories_inline_kb(categories, SelectCategoryTrackerCallback)
            await call.message.answer(text=select_category_text, reply_markup=markup)
    else:
        track_text = await traker_text(call, tracker)
        await call.message.answer(text=already_launch_tracker_text + track_text)
