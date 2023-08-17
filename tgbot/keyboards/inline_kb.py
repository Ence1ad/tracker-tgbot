from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import yes_btn, no_btn, exit_btn, cancel_btn
from tgbot.keyboards.callback_data_classes import CategoryCD, CategoryOperation, ActionOperation, ActionCD, \
    TrackerOperation, TrackerCD


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


async def list_inline_kb_with_cb_class(data_from_db: list, enum_val) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    if isinstance(enum_val, CategoryOperation):
        kb_builder_cat = await _categories(data_from_db, callback_class=CategoryCD, builder=kb_builder,
                                           operation=enum_val),
        kb_builder = kb_builder_cat[0]

    elif isinstance(enum_val, ActionOperation):
        kb_builder_act = await _actions(data_from_db, callback_class=ActionCD, builder=kb_builder, operation=enum_val),
        kb_builder = kb_builder_act[0]

    elif isinstance(enum_val, TrackerOperation):
        kb_builder_tra = await _tracker(data_from_db, callback_class=TrackerCD, builder=kb_builder, operation=enum_val)
        kb_builder = kb_builder_tra

    kb_builder.row(InlineKeyboardButton(text=exit_btn, callback_data=exit_btn))
    return kb_builder.as_markup()


async def _tracker(trackers: list, callback_class, builder, operation):
    for tracker in trackers:
        spend_hours = round(tracker.time_sum.seconds / 3600, 2)
        builder.button(
            text=f"{tracker.action_name} - {spend_hours}h",
            callback_data=callback_class(operation=operation, tracker_id=tracker.tracker_id)
        )
    builder.adjust(1)
    return builder


async def _actions(actions: list, callback_class, builder, operation):
    for act in actions:
        builder.button(
            text=f"{act.action_name}",
            callback_data=callback_class(operation=operation, action_id=act.action_id, action_name=act.action_name)
        )
    builder.adjust(2)
    return builder


async def _categories(categories: list, callback_class, builder, operation):
    for cat in categories:
        builder.button(
            text=f"{cat.category_name}",
            callback_data=callback_class(operation=operation, category_id=cat.category_id,
                                         category_name=cat.category_name)
        )
    builder.adjust(2)
    return builder
