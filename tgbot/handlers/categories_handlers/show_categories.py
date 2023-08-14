from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from db.categories.categories_commands import get_categories
from tgbot.keyboards.buttons_names import category_menu_buttons
from tgbot.keyboards.menu_kb import menu_inline_kb
from tgbot.utils.answer_text import empty_categories_text
from tgbot.utils.answer_text import show_categories_text, categories_options_text


async def get_categories_options(call: CallbackQuery):
    await call.message.delete()
    markup = await menu_inline_kb(category_menu_buttons)
    await call.message.answer(text=categories_options_text, reply_markup=markup)


async def display_categories(call: CallbackQuery):
    categories: list = list(await show_user_category(call))
    markup = await menu_inline_kb(category_menu_buttons)
    if categories:
        cats_in_column = ''
        for category in categories:
            cats_in_column += category.category_name + '\n\r'
        await call.message.answer(text=f"{show_categories_text}\n\r{cats_in_column}", reply_markup=markup)
    else:
        await call.message.answer(text=empty_categories_text, reply_markup=markup)


async def show_user_category(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    categories: ScalarResult = await get_categories(user_id)
    return categories
