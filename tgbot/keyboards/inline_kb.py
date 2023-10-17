from enum import IntEnum
from typing import Any

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner
from sqlalchemy import Row

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, \
    ActionOperation, ActionCD, TrackerOperation, TrackerCD


async def menu_inline_kb(
        buttons: dict[str, str], i18n: TranslatorRunner, is_cancel: bool = False
) -> InlineKeyboardMarkup:
    """Generate an inline keyboard with the specified buttons.

    :param buttons: dict[str, str]: A dictionary of button data in the format
    {callback_data: text}.
    :param i18n: TranslatorRunner: An instance of the translation runner for
    internationalization.
    :param is_cancel: bool, optional: Whether to include a cancel button. Defaults to
    False.
    :return: InlineKeyboardMarkup: The generated inline keyboard markup.
    """
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=i18n.get(str(data)), callback_data=data)
    kb_builder.adjust(2, 2, 1)
    if is_cancel:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(str(AppButtons.general_btn_source.CANCEL_BTN.name)),
            callback_data=AppButtons.general_btn_source.CANCEL_BTN.name)
        )
    else:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(str(AppButtons.general_btn_source.EXIT_BTN.name)),
            callback_data=AppButtons.general_btn_source.EXIT_BTN.name)
        )
    return kb_builder.as_markup()


async def callback_factories_kb(data_from_db: dict[str, str], enum_val: IntEnum
                                ) -> InlineKeyboardMarkup:
    """Generate an inline keyboard for callback factories.

    :param data_from_db: dict[str, str]): Data from a database query.
    :param enum_val: IntEnum: An IntEnum value representing the operation type.
    :raises KeyError: If the specified Enum value is not recognized.
    :return: InlineKeyboardMarkup: The generated inline keyboard markup.
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
    callback_dict = {
        CategoryOperation: CategoryCD,
        ActionOperation: ActionCD,
        TrackerOperation: TrackerCD
    }
    key: type[IntEnum] = type(enum_val)

    # noinspection PyTypeChecker
    callback_class = callback_dict.get(key)
    # noinspection PyTypeChecker
    callback_function = operation_callbacks[key]
    # Generate the keyboard using the appropriate callback function
    kb_builder = await callback_function(data_from_db,  # type: ignore
                                         callback_class=callback_class,
                                         builder=kb_builder,
                                         operation=enum_val)
    # Add an "Exit" button to the keyboard
    kb_builder.row(
        InlineKeyboardButton(text=AppButtons.general_btn_source.EXIT_BTN.value,
                             callback_data=AppButtons.general_btn_source.EXIT_BTN.name))
    return kb_builder.as_markup()


async def _tracker(
        trackers: list[Row[Any]], callback_class: type["TrackerCD"],
        builder: InlineKeyboardBuilder, operation: TrackerOperation
) -> InlineKeyboardBuilder:
    """Generate an inline keyboard for tracker-related operations.

    :param trackers: list[Row[Any]]: List of tracker data from a database query.
    :param callback_class: type["TrackerCD"]): The callback class for tracker-related
    operations.
    :param builder: InlineKeyboardBuilder: The keyboard builder to add buttons to.
    :param operation: TrackerOperation: The tracker operation type.
    :return: InlineKeyboardBuilder: The updated keyboard builder.
    """
    for tracker in trackers:
        spend_hours = round(tracker.duration.seconds / 3600, 2)
        builder.button(
            text=f"{tracker.action_name} - {spend_hours}h",
            callback_data=callback_class(operation=operation,
                                         tracker_id=tracker.tracker_id)
        )
    builder.adjust(1)
    return builder


async def _actions(
        actions: list[Row[Any]], callback_class: type["ActionCD"],
        builder: InlineKeyboardBuilder, operation: ActionOperation
) -> InlineKeyboardBuilder:
    """Generate an inline keyboard for action-related operations.

    This function is used internally to create action-related inline keyboards.
    :param actions: list[Row[Any]]: List of action data from a database query.
    :param callback_class: type["ActionCD"]: The callback class for action-related
     operations.
    :param builder: InlineKeyboardBuilder: The keyboard builder to add buttons to.
    :param operation: ActionOperation: The action operation type.
    :return: InlineKeyboardBuilder: The updated keyboard builder.
    """
    for act in actions:
        builder.button(
            text=f"{act.action_name}",
            callback_data=callback_class(operation=operation, action_id=act.action_id,
                                         action_name=act.action_name)
        )
    builder.adjust(2)
    return builder


async def _categories(categories: list[Row[Any]], callback_class: type["CategoryCD"],
                      builder: InlineKeyboardBuilder,
                      operation: CategoryOperation) -> InlineKeyboardBuilder:
    """Generate an inline keyboard for category-related operations.

    :param categories: list[Row[Any]]: List of category data from a database query.
    :param callback_class: type["CategoryCD"]: The callback class for category-related
     operations.
    :param builder: InlineKeyboardBuilder: The keyboard builder to add buttons to.
    :param operation: CategoryOperation: The category operation type.
    :return: InlineKeyboardBuilder: The updated keyboard builder.
    """
    for cat in categories:
        builder.button(
            text=f"{cat.category_name} ({cat.count})",
            callback_data=callback_class(
                operation=operation, category_id=cat.category_id,
                category_name=cat.category_name
            )
        )
    builder.adjust(2)
    return builder
