from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_upd_tracker
from db.operations.actions_operations import update_action_name, select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import ActionCD
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import ActionState
from tgbot.utils.validators import valid_name


async def prompt_new_action_name(
        call: CallbackQuery, state: FSMContext, callback_data: ActionCD,
        i18n: TranslatorRunner
) -> Message:
    """Handle prompting the user for a new name for an existing action.

    This handler is triggered when a user selects an action and prompts the user to
    enter a new name for the selected action.

    :param call: CallbackQuery: The user's callback query.
    :param state: FSMContext: The current state of the conversation.
    :param callback_data: ActionCD: The callback data containing action information.
    :param i18n: TranslatorRunner: The translator runner for handling
    internationalization.
    :return: Message: The response message to be sent to the user.
    """
    action_id: int = callback_data.action_id
    old_action_name: str = callback_data.action_name
    await state.update_data(action_id=action_id, old_action_name=old_action_name)
    await state.set_state(ActionState.UPDATE_NAME)

    return await call.message.edit_text(text=i18n.get('new_action_text'))


async def update_action_name_handler(
        message: Message, state: FSMContext, db_session: AsyncSession,
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Handle updating the name of an existing action.

    This handler is triggered when a user enters a new name for an existing action and
    updates the action name if the new name is valid.

    Handler Description:
    - Updates the action name in the state.
    - Validates if the new action name is unique within the category.
    - Updates the action name in the database if the name is valid.
    - Updates the action name in the Redis cache.
    :param message: Message: The user's message with the new action name.
    :param state: FSMContext: The current state of the conversation.
    :param db_session: AsyncSession: The database session for database operations.
    :param redis_client: Redis: The Redis client for caching operations.
    :param buttons: AppButtons: The app's button source.
    :param i18n: TranslatorRunner: The translator runner for handling
     internationalization.
    :return: Message: The response message to be sent to the user.
    """
    await state.update_data(action_name=message.text)
    user_id: int = message.from_user.id
    state_data: dict = await state.get_data()
    new_action_name: str = state_data['action_name']
    category_id: int = state_data['category_id']
    action_id: int = state_data['action_id']

    await state.set_state(ActionState.WAIT_CATEGORY_DATA)
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.actions_btn_source.action_menu_buttons(), i18n)

    if user_actions := await select_category_actions(user_id, category_id=category_id,
                                                     db_session=db_session):

        if new_valid_action_name := await valid_name(user_actions, new_action_name):
            await update_action_name(
                user_id=user_id, action_id=action_id,  db_session=db_session,
                new_action_name=new_valid_action_name,
            )
            await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client,
                                            value=1)
            await redis_upd_tracker(user_id=user_id, redis_client=redis_client,
                                    action_name=new_action_name)
            return await message.answer(text=i18n.get('upd_action_text'),
                                        reply_markup=markup)
        else:
            return await message.answer(
                text=i18n.get('action_exists_text', new_action_name=new_action_name),
                reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('valid_data_text'),
                                    reply_markup=markup)
