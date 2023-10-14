from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import redis_upd_tracker
from db.operations.actions_operations import update_action_name, select_category_actions
from tgbot.utils.validators import valid_name
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.callback_factories import ActionCD
from tgbot.utils.states import ActionState


async def prompt_new_action_name(call: CallbackQuery, state: FSMContext, callback_data: ActionCD, i18n: TranslatorRunner
                                 ) -> Message:
    """
    The prompt_new_action_name function is called when the user clicks on the &quot;Rename&quot; button in a
        list of actions. It prompts the user to enter a new name for an action, and then updates that
        action's name in the database.

    :param call: CallbackQuery: Get the callback query object from a callback inline button
    :param state: FSMContext: Store the state of the conversation
    :param callback_data: ActionCD: Get the action_id and action_name from the callback data
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the new_action_text

    """
    action_id: int = callback_data.action_id
    old_action_name: str = callback_data.action_name
    await state.update_data(action_id=action_id, old_action_name=old_action_name)
    await state.set_state(ActionState.UPDATE_NAME)

    return await call.message.edit_text(text=i18n.get('new_action_text'))


async def update_action_name_handler(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                                     redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The update_action_name_handler function is used to update the name of an action.

    :param message: Message: Get the message object that was sent by the user
    :param state: FSMContext: Store the state of the user in a conversation
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the redis client from the middleware. Update the user's tracker
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with a text about the successful update of the action name

    """
    await state.update_data(action_name=message.text)
    user_id: int = message.from_user.id
    state_data: dict = await state.get_data()
    new_action_name: str = state_data['action_name']
    category_id: int = state_data['category_id']
    action_id: int = state_data['action_id']

    await state.set_state(ActionState.WAIT_CATEGORY_DATA)
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.actions_btn_source.action_menu_buttons(), i18n)

    if user_actions := await select_category_actions(user_id, category_id=category_id, db_session=db_session):

        if new_valid_action_name := await valid_name(user_actions, new_action_name):
            await update_action_name(user_id=user_id, action_id=action_id, new_action_name=new_valid_action_name,
                                     db_session=db_session)
            await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client, value=1)
            await redis_upd_tracker(user_id=user_id, redis_client=redis_client, action_name=new_action_name)
            return await message.answer(text=i18n.get('upd_action_text'), reply_markup=markup)
        else:
            return await message.answer(text=i18n.get('action_exists_text', new_action_name=new_action_name),
                                        reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('valid_data_text'), reply_markup=markup)
