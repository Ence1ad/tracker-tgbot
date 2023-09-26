from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_upd_tracker, is_redis_hexists_tracker
from db.actions.actions_db_commands import update_action_name, select_category_actions
from tgbot.utils.validators import valid_name
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.callback_factories import ActionCD
from tgbot.utils.states import ActionState


async def prompt_new_action_name(call: CallbackQuery, state: FSMContext, callback_data: ActionCD, i18n: TranslatorRunner
                                 ) -> Message:
    action_id: int = callback_data.action_id
    old_action_name: str = callback_data.action_name
    await state.update_data(action_id=action_id, old_action_name=old_action_name)
    await state.set_state(ActionState.UPDATE_NAME)
    return await call.message.edit_text(text=i18n.get('new_action_text'))


async def upd_action(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                     redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    await state.update_data(action_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    new_action_name: str = state_data['action_name']
    category_id = state_data['category_id']
    action_id = state_data['action_id']
    category_name = state_data['category_name']
    # await state.clear()
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)
    await state.update_data(category_id=category_id, category_name=category_name)
    markup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
    # Is the text checking
    if not isinstance(new_action_name, str):
        return await message.answer(text=i18n.get('valid_action_name', new_line='\n'), reply_markup=markup)
    elif user_actions := await select_category_actions(user_id, category_id=category_id, db_session=db_session):  # If message a text

        if new_valid_action_name := await valid_name(user_actions, new_action_name):
            await update_action_name(user_id=user_id, action_id=action_id, new_action_name=new_valid_action_name,
                                     db_session=db_session)
            await redis_upd_tracker(user_id=user_id, redis_client=redis_client, action_name=new_action_name)
            return await message.answer(text=i18n.get('upd_action_text'), reply_markup=markup)
        else:
            return await message.answer(text=i18n.get('action_exists_text', new_action_name=new_action_name),
                                        reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('valid_data_text'), reply_markup=markup)
