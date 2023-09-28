from enum import IntEnum

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.actions.actions_db_commands import select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.states import ActionState


async def actions_main_menu_handler(
        call: CallbackQuery, callback_data: CategoryCD, state: FSMContext, buttons: AppButtons,
        i18n: TranslatorRunner, db_session: async_sessionmaker[AsyncSession]
) -> Message:

    """
    The actions_main_menu_handler function is a callback handler.
    It handles the user's choice of category and displays options for the actions in this category.
    If there are no actions, it displays an appropriate message.

    :param call: CallbackQuery: Get the callback query object from a callback inline button
    :param callback_data: CategoryCD: Extract the category_id and category_name from the callback data
    :param state: FSMContext: Store the state of the conversation
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner:  Get the language of the user from the middleware.
     Translate the buttons and the message text
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :return: A message with the text and the action menu buttons
    """
    user_id: int = call.from_user.id
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, category_name=category_name)
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)
    actions: list[Row] = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
    if actions:
        actions_list_text: str = await _actions_list(actions)
        return await call.message.edit_text(
            text=i18n.get('selected_category', category_name=category_name, new_line='\n',
                          actions_list_text=actions_list_text), reply_markup=markup
        )
    else:
        return await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)


async def display_actions(call: CallbackQuery, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                          buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The display_actions function handler displays all actions that belong to the category,
    and if there are no actions yet, it offers the user to create one.

    :param call: CallbackQuery: Get the callback query object from a callback inline button
    :param state: FSMContext: Store the data in the state machine
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: The action menu buttons and text of the message with a list of actions in the category
    """
    user_id: int = call.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    category_name: str = state_data['category_name']
    actions: list[Row] = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
        await call.message.delete()
        actions_list_text: str = await _actions_list(actions)
        return await call.message.answer(text=i18n.get('show_action_text', category_name=category_name,
                                         new_line='\n', actions_list_text=actions_list_text), reply_markup=markup)
    else:

        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.new_action(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)


async def _actions_list(model: list[Row]) -> str:
    """
    The _actions_list helper function takes a list of Row objects and returns a string.
    The string is formatted as follows:
        1. action_name_0\n\r2. action_name_1...etc.

    :param model: list[Row]: Pass the list of actions to the function
    :return: A string with all the actions in a list, numbered
    """
    act_column: str = ''.join([f"{idx}. {action.action_name}\n\r" for idx, action in enumerate(model, 1)])
    return act_column


async def collect_actions_data_handler(
        call: CallbackQuery, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:

    """
    The collect_actions_data_handler function is a callback handler.
    It handles pressed inline buttons and collect actions data to ActionCD Callback class

    :param call: CallbackQuery: Get the callback query object from a callback inline button
    :param state: FSMContext: Pass the state data to the function from the state machine
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text and the buttons based on callback data class
    """
    user_id: int = call.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    operation: IntEnum = await _get_action_operation(call_data=call.data, buttons=buttons)
    actions: list[Row] = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup: InlineKeyboardMarkup = await callback_factories_kb(actions, operation)
        return await call.message.edit_text(text=i18n.get('select_action_text'), reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)


async def _get_action_operation(call_data: str, buttons: AppButtons) -> IntEnum:
    """
    The _get_action_operation function is a helper function that returns an ActionOperation enum value based on the
    call_data parameter. The call_data parameter is expected to be one of the following:
        - UPDATE_ACTIONS (ActionOperation.UPD)
        - DELETE_ACTIONS (ActionOperation.DEL)

    :param call_data: str: Determine which button was pressed
    :param buttons: AppButtons: Get the buttons from the middleware
    :return: The operation that should be performed
    """
    operation: None = None
    if call_data == buttons.actions_data.UPDATE_ACTIONS.name:
        operation: IntEnum = ActionOperation.UPD
    elif call_data == buttons.actions_data.DELETE_ACTIONS.name:
        operation: IntEnum = ActionOperation.DEL
    return operation
