from enum import IntEnum

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.categories.categories_commands import select_categories, select_categories_with_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb


async def categories_main_menu_handler(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                                       buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The categories_main_menu_handler function is a handler for the categories main menu.
    It handles all the operations that can be performed on categories, such as creating new ones,
    editing existing ones and deleting them. It also allows to select category for user's tracker.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text and the action menu buttons
    """
    user_id: int = call.from_user.id
    operation: IntEnum = await _get_operation(call_data=call.data, buttons=buttons)
    if operation == CategoryOperation.READ_TRACKER:
        categories: list[Row] = await select_categories_with_actions(user_id, db_session)
    else:
        categories: list[Row] = await select_categories(user_id, db_session)
    if categories:
        markup: InlineKeyboardMarkup = await callback_factories_kb(categories, operation)
        return await call.message.edit_text(text=i18n.get('select_category_text'), reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.categories_btn_source.new_category(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_categories_text'), reply_markup=markup)


async def display_categories(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                             buttons: AppButtons, i18n: TranslatorRunner, state: FSMContext) -> Message:
    """
    The display_categories function is used to display the categories that a user has created.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :param state: FSMContext: Store the state of the conversation
    :return: The category menu buttons and the message text with a list of the categories
    """
    user_id: int = call.from_user.id
    await call.message.delete()
    await state.clear()
    categories: list[Row] = await select_categories(user_id, db_session)
    if categories:
        columns_list_text: str = await _categories_list(categories)
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.categories_btn_source.category_menu_buttons(),
                                                            i18n)
        return await call.message.answer(text=f"{i18n.get('show_categories_text')}\n\r{columns_list_text}",
                                         reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.categories_btn_source.new_category(), i18n)
        return await call.message.answer(text=i18n.get('empty_categories_text'), reply_markup=markup)


async def _categories_list(model: list[Row]) -> str:
    """
    The _categories_list helper function takes a list of Row objects and returns a string.
    The function iterates over the list of Row objects, appending each category_name to the cat_column variable.

    :param model: list[Row]: Pass in t: Pass in the list of categories from the database
    :return: A string of all the categories in the model
    """
    cat_column: str = ''.join([f"{idx}. {category.category_name}\n\r" for idx, category in enumerate(model, 1)])
    return cat_column


async def _get_operation(call_data: str, buttons: AppButtons) -> IntEnum:
    """
    The _get_operation function is a helper function that returns the operation to be performed
    on the category. It takes in two parameters: call_data and buttons. The call_data parameter
    is a string that represents the data of an inline keyboard button, while buttons is an instance
    of AppButtons class which contains all possible data for inline keyboard buttons.

    :param call_data: str: Determine which button was pressed
    :param buttons: AppButtons: Get the buttons from the middleware
    :return: The operation that should be performed
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
