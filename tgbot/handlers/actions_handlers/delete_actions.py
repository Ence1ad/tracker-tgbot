from aiogram.types import CallbackQuery

from db.actions.actions_db_commands import delete_action
from tgbot.keyboards.buttons_names import actions_menu_buttons
from tgbot.handlers.actions_handlers.show_actions import show_user_actions
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb

from tgbot.utils.answer_text import select_action_text, empty_actions_text, rm_action_text
from tgbot.keyboards.callback_factories import ActionOperation, ActionCD


async def select_remove_action(call: CallbackQuery):
    actions: list = list(await show_user_actions(call))
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.DEL)
        await call.message.answer(text=select_action_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(dict(create_actions='🆕 Create action'))
        await call.message.answer(text=empty_actions_text, reply_markup=markup)


async def del_action(call: CallbackQuery, callback_data: ActionCD):
    user_id = call.from_user.id
    # await call.message.delete()
    action_id = callback_data.action_id
    await delete_action(user_id, action_id)
    markup = await menu_inline_kb(actions_menu_buttons)
    await call.message.edit_text(text=f"{rm_action_text} {callback_data.action_name}", reply_markup=markup)
