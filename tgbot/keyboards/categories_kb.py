from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import user_categories, create_categories, update_categories, delete_categories


class DeleteCategoryCallback(CallbackData, prefix="del"):
    category_id: int
    category_name: str


class UpdateCategoryCallback(CallbackData, prefix="udp"):
    category_id: int
    category_name: str


async def categories_custom_inline_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text=user_categories, callback_data=user_categories)
    kb_builder.button(text=create_categories, callback_data=create_categories)
    kb_builder.button(text=update_categories, callback_data=update_categories)
    kb_builder.button(text=delete_categories, callback_data=delete_categories)
    kb_builder.adjust(2, 2)
    return kb_builder.as_markup()


async def remove_category_inline_kb(categories: list) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for cat in categories:
        kb_builder.button(
            text=f"{cat.category_name}",
            callback_data=DeleteCategoryCallback(category_id=cat.category_id, category_name=cat.category_name)
        )
    kb_builder.adjust(3)
    return kb_builder.as_markup()


async def update_category_inline_kb(categories: list) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for cat in categories:
        kb_builder.button(
            text=f"{cat.category_name}",
            callback_data=UpdateCategoryCallback(category_id=cat.category_id, category_name=cat.category_name)
        )
    kb_builder.adjust(3)
    return kb_builder.as_markup()
