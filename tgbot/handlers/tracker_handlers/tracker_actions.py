from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from cache.redis_cache import redis_client
from db.actions.actions_db_commands import get_user_actions_for_tracker
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import empty_actions_text, select_action_text
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation


async def display_actions_tracker(call: CallbackQuery, callback_data: CategoryCD):
    user_id = call.from_user.id
    print(callback_data.category_name)
    await redis_client.hset(name=user_id, key='category_name', value=callback_data.category_name)

    actions: list = list(await show_user_actions_tracker(call))
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.READ_TRACKER)
        await call.message.edit_text(
            text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{select_action_text}",
            reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_actions='🆕 Create action'))
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)


async def show_user_actions_tracker(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    category_name = (await redis_client.hget(name=user_id, key='category_name')).decode(encoding='utf-8')
    actions: ScalarResult = await get_user_actions_for_tracker(user_id, category_name=category_name)
    return actions
