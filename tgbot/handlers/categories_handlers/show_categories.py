from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.categories.categories_commands import select_categories

from tgbot.keyboards.buttons_names import category_menu_buttons, new_category_button
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import empty_categories_text, show_categories_text


async def display_categories(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession]
                             ) -> Message:
    user_id = call.from_user.id
    await call.message.delete()
    categories = await select_categories(user_id, db_session)
    if categories:
        cats_in_column = ''
        for idx, category in enumerate(categories, 1):
            cats_in_column += f"{idx}. {category.category_name}\n\r"
        markup = await menu_inline_kb(category_menu_buttons)
        return await call.message.answer(text=f"{show_categories_text}\n\r{cats_in_column}", reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_category_button)
        return await call.message.answer(text=empty_categories_text, reply_markup=markup)
