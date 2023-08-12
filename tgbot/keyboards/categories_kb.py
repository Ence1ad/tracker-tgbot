from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import user_categories, create_categories, update_categories, delete_categories


async def categories_menu_inline_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text=user_categories, callback_data=user_categories)
    kb_builder.button(text=create_categories, callback_data=create_categories)
    kb_builder.button(text=update_categories, callback_data=update_categories)
    kb_builder.button(text=delete_categories, callback_data=delete_categories)
    kb_builder.adjust(2, 2)
    return kb_builder.as_markup()


async def list_categories_inline_kb(categories: list, callback_class) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for cat in categories:
        kb_builder.button(
            text=f"{cat.category_name}",
            callback_data=callback_class(category_id=cat.category_id, category_name=cat.category_name)
        )
    kb_builder.adjust(3)
    return kb_builder.as_markup()
