from aiogram.types import CallbackQuery

from cache.redis_commands import redis_hget_category_id
from db.categories.categories_commands import select_categories, category_exists

from tgbot.keyboards.buttons_names import category_menu_buttons, new_category_button
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import empty_categories_text, show_categories_text


async def display_categories(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    categories: list = list(await select_categories(user_id))
    if categories:
        cats_in_column = ''
        for idx, category in enumerate(categories, 1):
            cats_in_column += f"{idx}. {category.category_name}\n\r"
        markup = await menu_inline_kb(category_menu_buttons)
        await call.message.answer(text=f"{show_categories_text}\n\r{cats_in_column}", reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_category_button)
        await call.message.answer(text=empty_categories_text, reply_markup=markup)


async def is_category_available(user_id: int, cb_category_id=None) -> bool:
    if cb_category_id:
        category_id = cb_category_id
    else:
        # Get category_id from cache
        category_id: int = await redis_hget_category_id(user_id)
    # Check if the category is available
    is_category = await category_exists(user_id, category_id)
    if not is_category:
        return True
    else:
        return False
