from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_hget_tracker_data, redis_delete_tracker
from db.actions.actions_db_commands import delete_action, select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb

from tgbot.utils.answer_text import empty_actions_text, rm_action_text, action_not_exists_text, \
    to_delete_action_text
from tgbot.keyboards.callback_factories import ActionOperation, ActionCD


async def select_remove_action(call: CallbackQuery, state: FSMContext,
                               db_session: async_sessionmaker[AsyncSession], buttons: AppButtons) -> None:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    await call.message.delete()
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.DEL)
        await call.message.answer(text=to_delete_action_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.new_action())
        await call.message.answer(text=empty_actions_text, reply_markup=markup)


async def del_action(call: CallbackQuery, callback_data: ActionCD, db_session: async_sessionmaker[AsyncSession],
                     redis_client: Redis, buttons: AppButtons) -> None:
    user_id = call.from_user.id
    action_id = callback_data.action_id
    markup = await menu_inline_kb(await buttons.action_menu_buttons())
    await redis_hget_tracker_data(user_id, redis_client, key="action_id") and await redis_delete_tracker(user_id,
                                                                                                         redis_client)
    returning = await delete_action(user_id, action_id, db_session)
    if returning:
        await call.message.edit_text(text=f"{rm_action_text} {callback_data.action_name}", reply_markup=markup)
    else:
        await call.message.edit_text(text=f"{action_not_exists_text} {callback_data.action_name}", reply_markup=markup)
