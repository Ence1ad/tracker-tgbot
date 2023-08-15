from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from db.actions.actions_db_commands import get_user_actions
from tgbot.handlers.actions_handlers.show_actions import USER_CATEGORY
from tgbot.keyboards.inline_kb import list_inline_kb_with_cb_class, menu_inline_kb
from tgbot.utils.answer_text import show_action_text, empty_actions_text
from tgbot.keyboards.callback_data_classes import SelectCategoryTrackerCallback, SelectActionTrackerCallback


async def display_actions_tracker(call: CallbackQuery, callback_data: SelectCategoryTrackerCallback):
    user_id = call.from_user.id
    USER_CATEGORY[user_id] = callback_data.category_id
    actions: list = list(await show_user_actions_tracker(call))
    if actions:
        markup = await list_inline_kb_with_cb_class(actions, SelectActionTrackerCallback)
        await call.message.answer(
            text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{show_action_text}",
            reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_actions='🆕 Create action'))
        await call.message.answer(text=empty_actions_text, reply_markup=markup)


async def show_user_actions_tracker(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    actions: ScalarResult = await get_user_actions(user_id, category_id=USER_CATEGORY[user_id])
    return actions
