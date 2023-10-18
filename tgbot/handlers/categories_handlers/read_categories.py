from enum import IntEnum

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from db.operations.categories_operations import select_categories, \
    select_categories_with_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb


async def categories_main_menu_handler(
        call: CallbackQuery, db_session: AsyncSession, buttons: AppButtons,
        i18n: TranslatorRunner
) -> Message:
    """Handle the main menu for categories.

    :param call: CallbackQuery: The callback query that triggered the main menu.
    :param db_session: AsyncSession: An asynchronous database session.
    :param buttons: AppButtons: An instance of the application buttons.
    :param i18n: TranslatorRunner: An instance of the translation runner for
    internationalization.
    :return: Message: A message with the category menu options.
    """
    user_id: int = call.from_user.id
    operation: IntEnum = await _get_operation(call_data=call.data, buttons=buttons)
    categories: Sequence = await select_categories(user_id, db_session)
    if categories and (operation != CategoryOperation.READ_TRACKER):
        markup: InlineKeyboardMarkup = await callback_factories_kb(categories,
                                                                   operation)
        return await call.message.edit_text(text=i18n.get('select_category_text'),
                                            reply_markup=markup)
    elif categories and (operation == CategoryOperation.READ_TRACKER):
        categories_with_actions: Sequence = await select_categories_with_actions(
            user_id, db_session)
        if not categories_with_actions:
            markup: InlineKeyboardMarkup = await menu_inline_kb(
                await buttons.general_btn_source.main_menu_buttons(),
                i18n)
            return await call.message.edit_text(
                text=i18n.get('empty_category_actions_text'), reply_markup=markup)
        else:
            markup: InlineKeyboardMarkup = await callback_factories_kb(
                categories_with_actions, operation)
            return await call.message.edit_text(text=i18n.get('select_category_text'),
                                                reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.categories_btn_source.new_category(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_categories_text'),
                                            reply_markup=markup)


async def display_categories(
        call: CallbackQuery, db_session: AsyncSession, buttons: AppButtons,
        i18n: TranslatorRunner, state: FSMContext
) -> Message:
    """Display the user's categories.

    :param call: CallbackQuery: The callback query that triggered the display of
    categories.
    :param db_session: AsyncSession: An asynchronous database session.
    :param buttons: AppButtons: An instance of the application buttons.
    :param i18n: TranslatorRunner: An instance of the translation runner for
     internationalization.
    :param state: FSMContext: The FSM (Finite State Machine) context for tracking the
     user's state.
    :return: Message: A message displaying the user's categories.
    """
    user_id: int = call.from_user.id
    await call.message.delete()
    await state.clear()
    categories: Sequence = await select_categories(user_id, db_session)
    if categories:
        columns_list_text: str = await _categories_list(categories)
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.categories_btn_source.category_menu_buttons(),
            i18n)
        return await call.message.answer(
            text=f"{i18n.get('show_categories_text')}\n\r{columns_list_text}",
            reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.categories_btn_source.new_category(), i18n)
        return await call.message.answer(text=i18n.get('empty_categories_text'),
                                         reply_markup=markup)


async def _categories_list(model: Sequence) -> str:
    """Create a formatted string representing a list of categories.

    :param model: model Sequence: A sequence of categories.
    :return:  str: A formatted string displaying the list of categories.
    """
    cat_column: str = ''.join(
        [f"{idx}. {category.category_name}\n\r" for idx, category in
         enumerate(model, 1)])
    return cat_column


async def _get_operation(call_data: str, buttons: AppButtons) -> IntEnum:
    """Determine the category operation based on the callback data.

    :param call_data: str: The callback data to be analyzed.
    :param buttons: AppButtons: An instance of the application buttons.
    :return: IntEnum: The determined category operation.
    """
    operation: None = None
    if call_data == buttons.general_btn_source.ACTIONS_BTN.name:
        operation: IntEnum = CategoryOperation.READ
    elif call_data == buttons.categories_btn_source.UPDATE_CATEGORIES.name:
        operation: IntEnum = CategoryOperation.UPD
    elif call_data == buttons.categories_btn_source.DELETE_CATEGORIES.name:
        operation: IntEnum = CategoryOperation.DEL
    elif call_data == buttons.trackers_btn_source.START_TRACKER_BTN.name:
        operation: IntEnum = CategoryOperation.READ_TRACKER
    return operation
