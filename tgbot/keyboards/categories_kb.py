from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def list_categories_inline_kb(categories: list, callback_class) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for cat in categories:
        kb_builder.button(
            text=f"{cat.category_name}",
            callback_data=callback_class(category_id=cat.category_id, category_name=cat.category_name)
        )
    kb_builder.adjust(3)
    return kb_builder.as_markup()
