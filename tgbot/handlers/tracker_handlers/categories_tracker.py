from aiogram.types import CallbackQuery

from db.categories.categories_commands import get_categories_without_actions
from db.tracker.tracker_db_command import get_launch_tracker
from db.tracker.tracker_model import Tracker
from tgbot.keyboards.inline_kb import stop_tracker_inline_kb, list_inline_kb_with_cb_class, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, traker_text, already_launch_tracker_text, \
    empty_categories_text
from tgbot.keyboards.callback_data_classes import SelectCategoryTrackerCallback


async def select_category_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    tracker = await get_launch_tracker(user_id)
    if not tracker:
        categories: list = list(await get_categories_without_actions(user_id))
        if categories:
            markup = await list_inline_kb_with_cb_class(categories, SelectCategoryTrackerCallback)
            await call.message.answer(text=select_category_text, reply_markup=markup)
        else:
            markup = await menu_inline_kb(dict(create_categories='🆕 Create category'))
            await call.message.answer(text=empty_categories_text, reply_markup=markup)
    else:
        markup = await stop_tracker_inline_kb()
        track_text = await traker_text(call, tracker)
        await call.message.answer(text=already_launch_tracker_text + track_text, reply_markup=markup)
