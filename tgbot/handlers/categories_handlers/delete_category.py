from aiogram.types import CallbackQuery

from db.categories.categories_commands import delete_category, select_categories
from tgbot.handlers.categories_handlers.show_categories import is_category_available
from tgbot.keyboards.buttons_names import category_menu_buttons, new_category_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import rm_category_text, select_category_text, empty_categories_text, \
    categories_is_fake_text
from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation


async def select_remove_category(call: CallbackQuery):
    user_id = call.from_user.id
    # await call.message.delete()
    categories: list = list(await select_categories(user_id))
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.DEL)
        await call.message.edit_text(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_category_button)
        await call.message.edit_text(text=empty_categories_text, reply_markup=markup)


async def del_category(call: CallbackQuery, callback_data: CategoryCD):
    user_id = call.from_user.id
    category_id = callback_data.category_id
    markup = await menu_inline_kb(category_menu_buttons)
    is_category: bool = await is_category_available(user_id, cb_category_id=category_id)
    if is_category:
        return await call.message.edit_text(text=categories_is_fake_text, reply_markup=markup)
    await delete_category(user_id, category_id)

    await call.message.edit_text(text=f"{rm_category_text} {callback_data.category_name}", reply_markup=markup)
