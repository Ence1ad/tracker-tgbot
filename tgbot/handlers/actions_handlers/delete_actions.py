from aiogram.types import CallbackQuery

from db.actions.actions_db_commands import delete_action
from tgbot.handlers.actions_handlers.show_actions import show_user_actions
from tgbot.keyboards.actions_kb import list_actions_inline_kb

from tgbot.utils.answer_text import select_action_text, empty_actions_text, rm_action_text
from tgbot.utils.callback_data_classes import DeleteActionCallback


async def select_remove_action(call: CallbackQuery):
    actions: list = list(await show_user_actions(call))
    if actions:
        markup = await list_actions_inline_kb(actions, DeleteActionCallback)
        await call.message.answer(text=select_action_text, reply_markup=markup)
    else:
        await call.message.answer(text=empty_actions_text)


async def del_action(call: CallbackQuery, callback_data: DeleteActionCallback):
    user_id = call.from_user.id
    await call.message.delete()
    action_id = callback_data.action_id
    await delete_action(user_id, action_id)
    await call.message.answer(text=f"{rm_action_text} {callback_data.action_name}")
