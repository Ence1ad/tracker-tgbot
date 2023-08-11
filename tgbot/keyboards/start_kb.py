from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import actions_btn, categories_btn, reports_btn, settings_btn,  \
    select_actions_btn


async def start_custom_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text=actions_btn, callback_data=select_actions_btn)
    kb_builder.button(text=categories_btn, callback_data=categories_btn)
    kb_builder.button(text=reports_btn, callback_data=reports_btn)
    kb_builder.button(text=settings_btn, callback_data=settings_btn)
    kb_builder.adjust(2, 2)
    return kb_builder.as_markup()
