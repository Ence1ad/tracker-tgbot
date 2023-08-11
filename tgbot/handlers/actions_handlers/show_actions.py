from aiogram.types import CallbackQuery
from sqlalchemy import ScalarResult

from db.actions.actions_db_commands import get_user_actions
from tgbot.handlers.actions_handlers.category import SelectCategoryCallback
from tgbot.keyboards.actions_kb import actions_inline_kb
from tgbot.utils.answer_text import empty_actions_text, categories_options_text, show_action_text

USER_CATEGORY = {}


async def get_actions_options(call: CallbackQuery, callback_data: SelectCategoryCallback):
    user_id = call.from_user.id
    USER_CATEGORY[user_id] = callback_data.category_id
    await call.message.delete()
    markup = await actions_inline_kb()
    await call.message.answer(text=categories_options_text, reply_markup=markup)


async def display_actions(call: CallbackQuery):
    actions: list = list(await show_user_actions(call))
    if actions:
        act_in_column = ''
        for action in actions:
            act_in_column += action.action_name + '\n\r'
        await call.message.answer(text=f"{show_action_text}\n\r{act_in_column}")
    else:
        await call.message.answer(text=empty_actions_text)


async def show_user_actions(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    actions: ScalarResult = await get_user_actions(user_id, category_id=USER_CATEGORY[user_id])
    return actions
