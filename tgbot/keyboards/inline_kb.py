from enum import Enum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, ActionOperation, ActionCD, \
    TrackerOperation, TrackerCD


async def start_menu_inline_kb(buttons: dict, i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=i18n.get(str(data)), callback_data=data)
    kb_builder.adjust(2, 2, 1)
    kb_builder.row(InlineKeyboardButton(text=i18n.get(str(AppButtons.general_data.CANCEL_BTN.name)),
                                        callback_data=AppButtons.general_data.CANCEL_BTN.name))
    return kb_builder.as_markup()


async def menu_inline_kb(buttons: dict, i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=i18n.get(str(data)), callback_data=data)
    kb_builder.adjust(2, 2, 1)
    kb_builder.row(InlineKeyboardButton(text=i18n.get(str(AppButtons.general_data.EXIT_BTN.name)),
                                        callback_data=AppButtons.general_data.EXIT_BTN.name))
    return kb_builder.as_markup()


async def callback_factories_kb(data_from_db: list, enum_val: Enum) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    get_kb = {
        CategoryOperation: _categories,
        ActionOperation: _actions,
        TrackerOperation: _tracker
    }
    callback_class = None
    if isinstance(enum_val, CategoryOperation):
        callback_class = CategoryCD

    elif isinstance(enum_val, ActionOperation):
        callback_class = ActionCD

    elif isinstance(enum_val, TrackerOperation):
        callback_class = TrackerCD

    kb_builder = await get_kb[enum_val.__class__](data_from_db, callback_class=callback_class, builder=kb_builder,
                                                  operation=enum_val)

    kb_builder.row(InlineKeyboardButton(text=AppButtons.general_data.EXIT_BTN.value,
                                        callback_data=AppButtons.general_data.EXIT_BTN.name))
    return kb_builder.as_markup()


async def _tracker(trackers: list,
                   callback_class: type[TrackerCD],
                   builder: InlineKeyboardBuilder,
                   operation: Enum
                   ) -> InlineKeyboardBuilder:
    for tracker in trackers:
        spend_hours = round(tracker.duration.seconds / 3600, 2)
        builder.button(
            text=f"{tracker.action_name} - {spend_hours}h",
            callback_data=callback_class(operation=operation, tracker_id=tracker.tracker_id)
        )
    builder.adjust(1)
    return builder


async def _actions(actions: list,
                   callback_class: type[ActionCD],
                   builder: InlineKeyboardBuilder,
                   operation: Enum) -> InlineKeyboardBuilder:
    for act in actions:
        builder.button(
            text=f"{act.action_name}",
            callback_data=callback_class(operation=operation, action_id=act.action_id, action_name=act.action_name)
        )
    builder.adjust(2)
    return builder


async def _categories(categories: list,
                      callback_class: type[CategoryCD],
                      builder: InlineKeyboardBuilder,
                      operation: Enum
                      ) -> InlineKeyboardBuilder:
    for cat in categories:
        builder.button(
            text=f"{cat.category_name} ({cat.count})",
            callback_data=callback_class(operation=operation, category_id=cat.category_id,
                                         category_name=cat.category_name)
        )
    builder.adjust(2)
    return builder
