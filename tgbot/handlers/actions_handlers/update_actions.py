from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_commands import redis_upd_tracker
from db.actions.actions_db_commands import update_action, select_category_actions
from tgbot.utils.validators import valid_name
from tgbot.keyboards.buttons_names import actions_menu_buttons, new_action_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import ActionOperation, ActionCD
from tgbot.utils.states import UpdateActionState, ActionState
from tgbot.utils.answer_text import new_action_text, empty_actions_text, upd_action_text, \
    accept_only_text, action_exists_text, action_not_exists_text, to_update_action_text


async def select_action(call: CallbackQuery, state: FSMContext, callback_data: ActionCD) -> None:
    await call.message.edit_text(text=new_action_text)
    action_id: int = callback_data.action_id
    await state.update_data(action_id=action_id)
    await state.set_state(UpdateActionState.GET_NAME)


async def update_action_reaction_handler(call: CallbackQuery, state: FSMContext,
                                         db_session: async_sessionmaker[AsyncSession]) -> None:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.UDP)
        await call.message.edit_text(text=to_update_action_text, reply_markup=markup)
        await state.set_state(UpdateActionState.GET_NAME)
    else:
        markup = await menu_inline_kb(new_action_button)
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)


async def upd_action(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                     redis_client: Redis) -> Message:
    await state.update_data(action_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    new_action_name: str = state_data['action_name']

    # Is the text checking
    if not new_action_name:
        await message.answer(text=f"{accept_only_text}")

    else:  # If message a text
        state_data = await state.get_data()
        category_id = state_data['category_id']
        user_actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        new_action_valid_name = await valid_name(user_actions, new_action_name)
        if new_action_valid_name:
            await state.set_state(ActionState.WAIT_CATEGORY_DATA)
            await _udp_action(message=message, redis_client=redis_client, state_data=state_data, db_session=db_session,
                              new_action_name=new_action_valid_name)
        else:
            return await message.answer(text=f"{new_action_name} {action_exists_text}")


async def _udp_action(message: Message, redis_client: Redis, state_data: dict[str: Any],
                      db_session: async_sessionmaker[AsyncSession], new_action_name: str) -> Message:
    user_id: int = message.from_user.id
    action_id = state_data['action_id']
    category_name = state_data['category_name']
    returning = await update_action(user_id=user_id, action_id=action_id,
                                    new_action_name=new_action_name, db_session=db_session)
    markup = await menu_inline_kb(actions_menu_buttons)
    if returning:
        await redis_upd_tracker(user_id=user_id, redis_client=redis_client, action_name=new_action_name)
        return await message.answer(
            text=f"{upd_action_text} - {new_action_name} for category - {category_name}",
            reply_markup=markup
        )
    else:
        return await message.answer(text=f"{action_not_exists_text}", reply_markup=markup)
