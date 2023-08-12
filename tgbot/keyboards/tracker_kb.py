from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import launched_btn, new_tracker_btn, day_track_btn, delete_tracker_btn, yes_btn, \
    no_btn


async def tracker_menu_inline_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text=launched_btn, callback_data=launched_btn)
    kb_builder.button(text=new_tracker_btn, callback_data=new_tracker_btn)
    kb_builder.button(text=day_track_btn, callback_data=day_track_btn)
    kb_builder.button(text=delete_tracker_btn, callback_data=delete_tracker_btn)
    kb_builder.adjust(2, 2)
    return kb_builder.as_markup()


async def stop_tracker_inline_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text=yes_btn, callback_data=yes_btn)
    kb_builder.button(text=no_btn, callback_data=no_btn)
    return kb_builder.as_markup()
