from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData

from db.categories.categories_commands import delete_category
from tgbot.handlers.categories_handlers import show_user_category
from tgbot.keyboards.categories_kb import list_categories_inline_kb
from tgbot.utils.answer_text import rm_category_text, select_category_text, empty_categories_text


class DeleteCategoryCallback(CallbackData, prefix="del"):
    category_id: int
    category_name: str


async def select_remove_category(call: CallbackQuery):
    categories: list = list(await show_user_category(call))
    if categories:
        markup = await list_categories_inline_kb(categories, DeleteCategoryCallback)
        await call.message.answer(text=select_category_text, reply_markup=markup)
    else:
        await call.message.answer(text=empty_categories_text)


async def del_category(call: CallbackQuery, callback_data: DeleteCategoryCallback):
    user_id = call.from_user.id
    await call.message.delete()
    category_id = callback_data.category_id
    await delete_category(user_id, category_id)
    await call.message.answer(text=f"{rm_category_text} {callback_data.category_name}")