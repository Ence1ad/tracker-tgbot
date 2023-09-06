from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_commands import redis_started_tracker
from db.categories.categories_commands import select_categories
from tgbot.keyboards.buttons_names import choice_buttons, new_category_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, already_launch_tracker_text, \
    empty_categories_text
from tgbot.keyboards.callback_factories import CategoryOperation


async def select_category_tracker(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    await call.message.delete()
    started_tracker = await redis_started_tracker(user_id)
    if not started_tracker:
        categories = await select_categories(user_id, db_session)
        if categories:
            markup = await callback_factories_kb(categories, CategoryOperation.READ_TRACKER)
            await call.message.answer(text=select_category_text, reply_markup=markup)
        else:
            markup = await menu_inline_kb(new_category_button)
            await call.message.answer(text=empty_categories_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(choice_buttons)
        await call.message.answer(text=already_launch_tracker_text + started_tracker, reply_markup=markup)
