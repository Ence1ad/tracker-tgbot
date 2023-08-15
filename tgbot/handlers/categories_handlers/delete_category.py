from aiogram.types import CallbackQuery

from db.categories.categories_commands import delete_category, get_categories_without_actions
from tgbot.keyboards.buttons_names import category_menu_buttons
from tgbot.keyboards.inline_kb import list_inline_kb_with_cb_class, menu_inline_kb
from tgbot.utils.answer_text import rm_category_text, select_category_text, empty_categories_text
from tgbot.keyboards.callback_data_classes import DeleteCategoryCallback


async def select_remove_category(call: CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    categories: list = list(await get_categories_without_actions(user_id))
    if categories:
        markup = await list_inline_kb_with_cb_class(categories, DeleteCategoryCallback)
        await call.message.answer(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_categories='🆕 Create category'))
        await call.message.answer(text=empty_categories_text, reply_markup=markup)


async def del_category(call: CallbackQuery, callback_data: DeleteCategoryCallback):
    user_id = call.from_user.id
    await call.message.delete()
    category_id = callback_data.category_id
    await delete_category(user_id, category_id)
    markup = await menu_inline_kb(category_menu_buttons)
    await call.message.answer(text=f"{rm_category_text} {callback_data.category_name}", reply_markup=markup)
