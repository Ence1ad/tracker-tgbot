from aiogram.types import CallbackQuery

from db.categories.categories_commands import get_categories_without_actions
from tgbot.keyboards.inline_kb import list_inline_kb_with_cb_class, menu_inline_kb
from tgbot.utils.answer_text import select_category_text, empty_categories_text
from tgbot.keyboards.callback_data_classes import CategoryOperation


async def select_category(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    categories: list = list(await get_categories_without_actions(user_id))
    if categories:
        markup = await list_inline_kb_with_cb_class(categories, CategoryOperation.READ)
        await call.message.answer(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_categories='🆕 Create category'))
        await call.message.answer(text=empty_categories_text, reply_markup=markup)
