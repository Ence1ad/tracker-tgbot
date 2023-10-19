from collections.abc import Sequence
from enum import IntEnum

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from db.operations.actions_operations import select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.utils.states import ActionState


async def actions_main_menu_handler(
        call: CallbackQuery, callback_data: CategoryCD, state: FSMContext,
        buttons: AppButtons, i18n: TranslatorRunner, db_session: AsyncSession
) -> Message:
    """Handle category-related actions from the main menu.

    This handler is triggered when a user selects a category-related action from the
    main menu. It displays the selected category and related actions to the user.

    :param call: CallbackQuery: The user's callback query.
    :param callback_data: CategoryCD: The category data from the user's selection.
    :param state: FSMContext: The current state of the conversation.
    :param buttons: AppButtons: The app's button source.
    :param i18n: TranslatorRunner: The translator runner for handling
     internationalization.
    :param db_session: AsyncSession: The database session for database operations.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = call.from_user.id
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, category_name=category_name)
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)
    actions: Sequence = await select_category_actions(user_id, category_id=category_id,
                                                      db_session=db_session)
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.actions_btn_source.action_menu_buttons(), i18n
    )
    if actions:
        actions_list_text: str = await _actions_list(actions)
        return await call.message.edit_text(
            text=i18n.get('selected_category', category_name=category_name,
                          new_line='\n',
                          actions_list_text=actions_list_text), reply_markup=markup
        )
    else:
        return await call.message.edit_text(text=i18n.get('empty_actions_text'),
                                            reply_markup=markup)


async def display_actions(
        call: CallbackQuery, state: FSMContext, db_session: AsyncSession,
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Display the user's category actions.

    This handler is triggered when a user selects the "Show Actions" button to display
    their category actions. It shows the user's category actions and allows them to
    perform further actions on these actions.

    :param call: CallbackQuery: The user's callback query.
    :param state: FSMContext: The current state of the conversation.
    :param db_session: AsyncSession: The database session for database operations.
    :param buttons: AppButtons: The app's button source.
    :param i18n: TranslatorRunner: The translator runner for handling
    internationalization.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = call.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    category_name: str = state_data['category_name']
    actions: Sequence = await select_category_actions(user_id, category_id=category_id,
                                                      db_session=db_session)
    if actions:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.actions_btn_source.action_menu_buttons(),
            i18n)
        await call.message.delete()
        actions_list_text: str = await _actions_list(actions)
        return await call.message.answer(
            text=i18n.get('show_action_text', category_name=category_name,
                          new_line='\n', actions_list_text=actions_list_text),
            reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.actions_btn_source.new_action(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_actions_text'),
                                            reply_markup=markup)


async def _actions_list(model: Sequence) -> str:
    """Collect and formats a list of category actions for display.

    :param model: Sequence: A sequence of category actions to display.
    :return: str: The formatted list of category actions.
    """
    act_column: str = ''.join([f"{idx}. {action.action_name}\n\r" for idx, action
                               in enumerate(model, 1)])
    return act_column


async def collect_actions_data_handler(
        call: CallbackQuery, state: FSMContext, db_session: AsyncSession,
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Collect and displays category actions for user selection.

    This handler is triggered when a user selects an action-related operation for
    category actions. It collects and displays the available category actions and
    allows the user to perform actions on them.

    :param call: CallbackQuery: The user's callback query.
    :param state: FSMContext: The current state of the conversation.
    :param db_session: AsyncSession: The database session for database operations.
    :param buttons: AppButtons: The app's button source.
    :param i18n: TranslatorRunner: The translator runner for handling
     internationalization.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = call.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']

    actions: Sequence = await select_category_actions(user_id, category_id=category_id,
                                                      db_session=db_session)
    if actions:
        operation: IntEnum = await _get_action_operation(call_data=call.data,
                                                         buttons=buttons)
        markup: InlineKeyboardMarkup = await callback_factories_kb(actions, operation)
        return await call.message.edit_text(text=i18n.get('select_action_text'),
                                            reply_markup=markup)
    else:
        await call.message.delete()
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.actions_btn_source.action_menu_buttons(), i18n
        )
        return await call.message.answer(text=i18n.get('empty_actions_text'),
                                         reply_markup=markup)


async def _get_action_operation(call_data: str, buttons: AppButtons) -> IntEnum:
    """Get the action operation from the user's callback data.

    :param call_data: str: The callback data from the user's selection.
    :param buttons: AppButtons: The app's button source.
    :return: IntEnum: The action operation based on the user's selection.
    """
    operation: None = None
    if call_data == buttons.actions_btn_source.UPDATE_ACTIONS.name:
        operation: IntEnum = ActionOperation.UPD
    elif call_data == buttons.actions_btn_source.DELETE_ACTIONS.name:
        operation: IntEnum = ActionOperation.DEL
    return operation
