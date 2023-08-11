from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

from tgbot.handlers.categories_handlers import show_user_category
from tgbot.utils.answer_text import select_category_text
from tgbot.keyboards.categories_kb import list_categories_inline_kb



class SelectCategoryCallback(CallbackData, prefix="sel"):
    category_id: int
    category_name: str


async def select_category(call: CallbackQuery):
    categories: list = list(await show_user_category(call))
    if categories:
        markup = await list_categories_inline_kb(categories, SelectCategoryCallback)
        await call.message.answer(text=select_category_text, reply_markup=markup)
