from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.categories.categories_commands import select_categories
from tgbot.keyboards.buttons_names import new_category_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, empty_categories_text
from tgbot.keyboards.callback_factories import CategoryOperation


async def select_category(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    categories = await select_categories(user_id, db_session)
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.READ)
        await call.message.edit_text(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_category_button)
        await call.message.edit_text(text=empty_categories_text, reply_markup=markup)
