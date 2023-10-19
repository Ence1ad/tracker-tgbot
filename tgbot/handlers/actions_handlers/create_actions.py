from collections.abc import Sequence

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.operations.actions_operations import create_actions, select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import ActionState
from tgbot.utils.validators import valid_name


async def prompt_name_4_new_action_handler(
        call: CallbackQuery, state: FSMContext, i18n: TranslatorRunner,
        db_session: AsyncSession,
        buttons: AppButtons
) -> Message:
    """Handle prompting the user for a name for a new action.

    This handler is triggered when a user selects the "New Action" button and prompts
    the user to enter a name for the new action.

    :param call: CallbackQuery: The user's callback query.
    :param state: FSMContext: The current state of the conversation.
    :param i18n: TranslatorRunner: The translator runner for handling
    internationalization.
    :param db_session: AsyncSession: The database session for database operations.
    :param buttons: AppButtons: The app's button source.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = call.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']

    # Get user_actions from db
    action_count: int = len(
        await select_category_actions(user_id, category_id, db_session)
    )
    if action_count >= settings.USER_ACTIONS_LIMIT:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.actions_btn_source.action_menu_buttons(),
            i18n)
        return await call.message.edit_text(
            text=i18n.get('action_limit_text',
                          action_limit=settings.USER_ACTIONS_LIMIT),
            reply_markup=markup)
    else:
        await state.set_state(ActionState.GET_NAME)
        return await call.message.edit_text(text=i18n.get('new_action_text'))


async def create_action_handler(
        message: Message, state: FSMContext,
        db_session: AsyncSession, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Handle creating a new action.

    This handler is triggered when a user enters the name for a new action and creates
    the new action if the name is valid.

    :param message: Message: The user's message with the name for the new action.
    :param state: FSMContext: The current state of the conversation.
    :param db_session: AsyncSession: The database session for database operations.
    :param buttons: AppButtons: The app's button source.
    :param i18n: TranslatorRunner: The translator runner for handling
     internationalization.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = message.from_user.id
    await state.update_data(action_name=message.text)
    state_data: dict = await state.get_data()
    # Get category_id from cache
    category_id: int = state_data['category_id']
    new_action_name: str = state_data['action_name']
    # If message not a text message
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.actions_btn_source.action_menu_buttons(), i18n)
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)

    user_actions: Sequence = await select_category_actions(user_id,
                                                           category_id=category_id,
                                                           db_session=db_session)
    if new_action_valid_name := await valid_name(user_actions, new_action_name):
        await create_actions(user_id, new_action_valid_name, category_id=category_id,
                             db_session=db_session)
        return await message.answer(text=i18n.get(
            'added_new_action_text', new_action_valid_name=new_action_valid_name),
                                    reply_markup=markup)
    else:
        return await message.answer(
            text=i18n.get('action_exists_text', new_action_name=new_action_name),
            reply_markup=markup)
