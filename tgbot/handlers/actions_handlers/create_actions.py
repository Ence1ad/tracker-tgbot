from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from db.operations.actions_operations import create_actions, select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import ActionState
from tgbot.utils.validators import valid_name


async def prompt_name_4_new_action_handler(
        call: CallbackQuery, state: FSMContext,  i18n: TranslatorRunner, db_session: async_sessionmaker[AsyncSession],
        buttons: AppButtons
) -> Message:
    """
    The prompt_name_4_new_action_handler function is a callback handler for the 'new_action' button.
    It checks if the user has reached his limit of actions per category and, if not, prompts him to enter a name for
    the new action.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param state: FSMContext: Pass the state data to the function from the state machine
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and text of the message
    :param db_session: async_sessionmaker[AsyncSession]:  Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :return:  A message with the text and the action menu buttons
    """
    user_id: int = call.from_user.id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']

    # Get user_actions from db
    action_count: int = len(await select_category_actions(user_id, category_id, db_session))
    if action_count >= settings.USER_ACTIONS_LIMIT:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.actions_btn_source.action_menu_buttons(),
                                                            i18n)
        return await call.message.edit_text(
            text=i18n.get('action_limit_text', action_limit=settings.USER_ACTIONS_LIMIT), reply_markup=markup)
    else:
        await state.set_state(ActionState.GET_NAME)
        return await call.message.edit_text(text=i18n.get('new_action_text'))


async def create_action_handler(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                                buttons: AppButtons,  i18n: TranslatorRunner) -> Message:
    """
    The create_action_handler function is responsible for creating a new action in the database.

    :param message: Message: Get the message object that was sent by the user
    :param state: FSMContext: Store the current state of the conversation
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text and the action menu buttons
    """
    user_id: int = message.from_user.id
    await state.update_data(action_name=message.text)
    state_data: dict = await state.get_data()
    # Get category_id from cache
    category_id: int = state_data['category_id']
    new_action_name: str = state_data['action_name']
    # If message not a text message
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.actions_btn_source.action_menu_buttons(), i18n)
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)

    user_actions: list[Row] = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if new_action_valid_name := await valid_name(user_actions, new_action_name):
        await create_actions(user_id, new_action_valid_name, category_id=category_id, db_session=db_session)
        return await message.answer(text=i18n.get('added_new_action_text',
                                                  new_action_valid_name=new_action_valid_name),
                                    reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('action_exists_text', new_action_name=new_action_name),
                                    reply_markup=markup)
