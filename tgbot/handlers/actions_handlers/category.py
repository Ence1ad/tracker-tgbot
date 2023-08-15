from aiogram.types import CallbackQuery

from db.categories.categories_commands import get_categories_without_actions
from tgbot.keyboards.menu_kb import menu_inline_kb
from tgbot.utils.answer_text import select_category_text, empty_categories_text
from tgbot.keyboards.categories_kb import list_categories_inline_kb
from tgbot.utils.callback_data_classes import SelectCategoryCallback


async def select_category(call: CallbackQuery):
    user_id = call.from_user.id
    categories: list = list(await get_categories_without_actions(user_id))
    if categories:
        markup = await list_categories_inline_kb(categories, SelectCategoryCallback)
        await call.message.answer(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_categories='🆕 Create category'))
        await call.message.answer(text=empty_categories_text, reply_markup=markup)
