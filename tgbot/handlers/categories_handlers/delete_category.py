from aiogram.types import CallbackQuery

from db.categories.categories_commands import delete_category, select_categories
from tgbot.keyboards.buttons_names import category_menu_buttons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import rm_category_text, select_category_text, empty_categories_text
from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation


async def select_remove_category(call: CallbackQuery):
    user_id = call.from_user.id
    # await call.message.delete()
    categories: list = list(await select_categories(user_id))
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.DEL)
        await call.message.edit_text(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_categories='🆕 Create category'))
        await call.message.edit_text(text=empty_categories_text, reply_markup=markup)


async def del_category(call: CallbackQuery, callback_data: CategoryCD):
    user_id = call.from_user.id
    # await call.message.delete()
    category_id = callback_data.category_id
    await delete_category(user_id, category_id)
    markup = await menu_inline_kb(category_menu_buttons)
    await call.message.edit_text(text=f"{rm_category_text} {callback_data.category_name}", reply_markup=markup)
