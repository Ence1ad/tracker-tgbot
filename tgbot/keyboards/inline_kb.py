from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import yes_btn, no_btn, exit_btn, cancel_btn
from tgbot.keyboards.callback_data_classes import DeleteTrackerCallback, SelectActionTrackerCallback, \
    DeleteActionCallback, UpdateActionCallback, SelectCategoryCallback, DeleteCategoryCallback, \
    UpdateCategoryCallback, SelectCategoryTrackerCallback


async def start_menu_inline_kb(buttons: dict) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=txt, callback_data=data)
    kb_builder.adjust(2, 2, 1)
    kb_builder.row(InlineKeyboardButton(text=cancel_btn, callback_data=cancel_btn))
    return kb_builder.as_markup()


async def menu_inline_kb(buttons: dict) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=txt, callback_data=data)
    kb_builder.adjust(2, 2, 1)
    kb_builder.row(InlineKeyboardButton(text=exit_btn, callback_data=exit_btn))
    return kb_builder.as_markup()


async def stop_tracker_inline_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text=yes_btn, callback_data=yes_btn)
    kb_builder.button(text=no_btn, callback_data=no_btn)
    return kb_builder.as_markup()


async def list_inline_kb_with_cb_class(data_from_db: list, callback_class) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    get_buttons_with_callback_data = {
        DeleteTrackerCallback: _tracker,
        SelectActionTrackerCallback: _actions,
        DeleteActionCallback: _actions,
        UpdateActionCallback: _actions,
        SelectCategoryCallback: _categories,
        DeleteCategoryCallback: _categories,
        UpdateCategoryCallback: _categories,
        SelectCategoryTrackerCallback: _categories,
    }
    kb_builder = await get_buttons_with_callback_data[callback_class](data_from_db, callback_class, builder=kb_builder)
    kb_builder.row(InlineKeyboardButton(text=exit_btn, callback_data=exit_btn))
    return kb_builder.as_markup()


async def _tracker(trackers: list, callback_class, builder):
    for tracker in trackers:
        spend_hours = round(tracker.time_sum.seconds / 3600, 2)
        builder.button(
            text=f"{tracker.action_name} - {spend_hours}h",
            callback_data=callback_class(tracker_id=tracker.tracker_id)
        )
    builder.adjust(1)
    return builder


async def _actions(actions: list, callback_class, builder):
    for act in actions:
        builder.button(
            text=f"{act.action_name}",
            callback_data=callback_class(action_id=act.action_id, action_name=act.action_name)
        )
    builder.adjust(2)
    return builder


async def _categories(categories: list, callback_class, builder):
    for cat in categories:
        builder.button(
            text=f"{cat.category_name}",
            callback_data=callback_class(category_id=cat.category_id, category_name=cat.category_name)
        )
    builder.adjust(2)
    return builder
