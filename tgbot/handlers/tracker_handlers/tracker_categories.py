from aiogram.types import CallbackQuery

from db.categories.categories_commands import select_categories
from db.tracker.tracker_db_command import select_started_tracker
from tgbot.keyboards.buttons_names import choice_buttons, new_category_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, tracker_text, already_launch_tracker_text, \
    empty_categories_text
from tgbot.keyboards.callback_factories import CategoryOperation


async def select_category_tracker(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    tracker = await select_started_tracker(user_id)
    if not tracker:
        categories: list = list(await select_categories(user_id))
        if categories:
            markup = await callback_factories_kb(categories, CategoryOperation.READ_TRACKER)
            await call.message.answer(text=select_category_text, reply_markup=markup)
        else:
            markup = await menu_inline_kb(new_category_button)
            await call.message.answer(text=empty_categories_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(choice_buttons)
        track_text = await tracker_text(call, tracker)
        await call.message.answer(text=already_launch_tracker_text + track_text, reply_markup=markup)
