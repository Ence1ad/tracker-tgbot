from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import yes_btn, no_btn


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
