from datetime import timedelta

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


async def list_trackers_inline_kb(trackers: list, callback_class) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for tracker in trackers:
        spend_hours = round(tracker.time_sum.seconds / 3600, 2)
        kb_builder.button(
            text=f"{tracker.action_name} - {spend_hours}h",
            callback_data=callback_class(tracker_id=tracker.tracker_id)
        )
    kb_builder.adjust(1)
    return kb_builder.as_markup()
