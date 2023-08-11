from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from db.categories.categories_commands import get_categories
from tgbot.utils.answer_text import empty_categories_text
from tgbot.keyboards.categories_kb import categories_menu_inline_kb
from tgbot.utils.answer_text import show_categories_text, categories_options_text


async def get_categories_options(call: CallbackQuery):
    await call.message.delete()
    markup = await categories_menu_inline_kb()
    await call.message.answer(text=categories_options_text, reply_markup=markup)


async def display_categories(call: CallbackQuery):
    categories: list = list(await show_user_category(call))
    if categories:
        cats_in_column = ''
        for category in categories:
            cats_in_column += category.category_name + '\n\r'
        await call.message.answer(text=f"{show_categories_text}\n\r{cats_in_column}")
    else:
        await call.message.answer(text=empty_categories_text)


async def show_user_category(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    categories: ScalarResult = await get_categories(user_id)
    return categories
