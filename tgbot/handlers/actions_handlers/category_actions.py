from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.categories.categories_commands import select_categories
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, empty_categories_text
from tgbot.keyboards.callback_factories import CategoryOperation


async def select_category(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession], buttons: AppButtons
                          ) -> Message:
    user_id = call.from_user.id
    categories = await select_categories(user_id, db_session)
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.READ)
        return await call.message.edit_text(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.new_category())
        return await call.message.edit_text(text=empty_categories_text, reply_markup=markup)
