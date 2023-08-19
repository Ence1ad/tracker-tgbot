from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from db.actions.actions_db_commands import get_user_actions_for_tracker
from tgbot.handlers.actions_handlers.show_actions import USER_CATEGORY_NAME
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import show_action_text, empty_actions_text
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation


async def display_actions_tracker(call: CallbackQuery, callback_data: CategoryCD):
    user_id = call.from_user.id
    USER_CATEGORY_NAME[user_id] = callback_data.category_name
    actions: list = list(await show_user_actions_tracker(call))
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.READ_TRACKER)
        await call.message.answer(
            text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{show_action_text}",
            reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_actions='🆕 Create action'))
        await call.message.answer(text=empty_actions_text, reply_markup=markup)


async def show_user_actions_tracker(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    actions: ScalarResult = await get_user_actions_for_tracker(user_id, category_name=USER_CATEGORY_NAME[user_id])
    return actions
