from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from db.actions.actions_db_commands import get_user_actions
from tgbot.keyboards.actions_kb import list_actions_inline_kb
from tgbot.utils.answer_text import show_action_text, empty_actions_text
from tgbot.utils.callback_data_classes import SelectCategoryTrackerCallback, SelectActionTrackerCallback

USER_TRACKER_CATEGORY = {}


async def display_actions_tracker(call: CallbackQuery, callback_data: SelectCategoryTrackerCallback):
    user_id = call.from_user.id
    USER_TRACKER_CATEGORY[user_id] = callback_data.category_id
    actions: list = list(await show_user_actions_tracker(call))
    if actions:
        markup = await list_actions_inline_kb(actions, SelectActionTrackerCallback)
        await call.message.answer(
            text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{show_action_text}",
            reply_markup=markup)
    else:
        await call.message.answer(text=empty_actions_text)


async def show_user_actions_tracker(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    actions: ScalarResult = await get_user_actions(user_id, category_id=USER_TRACKER_CATEGORY[user_id])
    return actions
