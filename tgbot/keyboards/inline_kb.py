from enum import IntEnum
from typing import Type

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
    kb_builder.row(InlineKeyboardButton(text=i18n.get(str(AppButtons.general_btn_source.CANCEL_BTN.name)),
                                        callback_data=AppButtons.general_btn_source.CANCEL_BTN.name))
    return kb_builder.as_markup()


async def menu_inline_kb(buttons: dict, i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=i18n.get(str(data)), callback_data=data)
    kb_builder.adjust(2, 2, 1)
    kb_builder.row(InlineKeyboardButton(text=i18n.get(str(AppButtons.general_btn_source.EXIT_BTN.name)),
                                        callback_data=AppButtons.general_btn_source.EXIT_BTN.name))
    return kb_builder.as_markup()


async def callback_factories_kb(data_from_db: list, enum_val: IntEnum) -> InlineKeyboardMarkup:
    """
   Generates an InlineKeyboardMarkup for a specific operation based on data and context.

   :param list data_from_db: A list of data related to the operation.
   :param Enum enum_val: The Enum representing the operation type.

   :returns: The generated InlineKeyboardMarkup with inline buttons.
    """
    # Create an InlineKeyboardBuilder to build the keyboard
    kb_builder = InlineKeyboardBuilder()

    # Define a mapping of operation Enums to callback functions
    operation_callbacks = {
        CategoryOperation: _categories,
        ActionOperation: _actions,
        TrackerOperation: _tracker
    }
    # Determine the appropriate callback class based on the Enum
    callback_class = {
        CategoryOperation: CategoryCD,
        ActionOperation: ActionCD,
        TrackerOperation: TrackerCD
    }.get(type(enum_val))
    # Generate the keyboard using the appropriate callback function
    kb_builder = await operation_callbacks[type(enum_val)](data_from_db, callback_class=callback_class,
                                                           builder=kb_builder, operation=enum_val)
    # Add an "Exit" button to the keyboard
    kb_builder.row(InlineKeyboardButton(text=AppButtons.general_btn_source.EXIT_BTN.value,
                                        callback_data=AppButtons.general_btn_source.EXIT_BTN.name))
    return kb_builder.as_markup()


async def _tracker(trackers: list, callback_class: Type["TrackerCD"], builder: InlineKeyboardBuilder, operation: IntEnum
                   ) -> InlineKeyboardBuilder:
    """
     Generates inline keyboard buttons for trackers based on the provided list.

   :param list trackers: A list of tracker objects.
   :param Type["TrackerCD"] callback_class: The callback class representing tracker-related actions.
   :param InlineKeyboardBuilder builder: The InlineKeyboardBuilder object to build the keyboard.
   :param Enum operation: The operation IntEnum representing the context or action related to this keyboard.

   :returns: The updated InlineKeyboardBuilder object containing the generated buttons.
    """
    for tracker in trackers:
        spend_hours = round(tracker.duration.seconds / 3600, 2)
        builder.button(
            text=f"{tracker.action_name} - {spend_hours}h",
            callback_data=callback_class(operation=operation, tracker_id=tracker.tracker_id)
        )
    builder.adjust(1)
    return builder


async def _actions(actions: list, callback_class: Type["ActionCD"], builder: InlineKeyboardBuilder, operation: IntEnum
                   ) -> InlineKeyboardBuilder:
    """
    Generates inline keyboard buttons for actions based on the provided list.

   :param list actions: A list of action objects.
   :param Type["ActionCD"] callback_class: The callback class representing action-related actions.
   :param InlineKeyboardBuilder builder: The InlineKeyboardBuilder object to build the keyboard.
   :param Enum operation: The operation IntEnum representing the context or action related to this keyboard.

   :returns: The updated InlineKeyboardBuilder object containing the generated buttons.
    """
    for act in actions:
        builder.button(
            text=f"{act.action_name}",
            callback_data=callback_class(operation=operation, action_id=act.action_id, action_name=act.action_name)
        )
    builder.adjust(2)
    return builder


async def _categories(categories: list, callback_class: Type["CategoryCD"], builder: InlineKeyboardBuilder,
                      operation: IntEnum) -> InlineKeyboardBuilder:
    """
    Generates inline keyboard buttons for categories based on the provided list.

   :param list categories: A list of category objects.
   :param Type["CategoryCD"] callback_class: The callback class representing category-related actions.
   :param InlineKeyboardBuilder builder: The InlineKeyboardBuilder object to build the keyboard.
   :param Enum operation: The operation IntEnum representing the context or action related to this keyboard.

   :returns: The updated InlineKeyboardBuilder object containing the generated buttons.
    """
    for cat in categories:
        builder.button(
            text=f"{cat.category_name} ({cat.count})",
            callback_data=callback_class(operation=operation, category_id=cat.category_id,
                                         category_name=cat.category_name)
        )
    builder.adjust(2)
    return builder
