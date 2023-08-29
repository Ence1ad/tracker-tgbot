from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from db.actions.actions_db_commands import delete_action, select_category_actions
from tgbot.keyboards.buttons_names import actions_menu_buttons, new_action_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb

from tgbot.utils.answer_text import empty_actions_text, rm_action_text, action_not_exists_text, \
    to_delete_action_text
from tgbot.keyboards.callback_factories import ActionOperation, ActionCD


async def select_remove_action(call: CallbackQuery, state: FSMContext) -> None:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    actions = await select_category_actions(user_id, category_id=category_id)
    await call.message.delete()
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.DEL)
        await call.message.answer(text=to_delete_action_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_action_button)
        await call.message.answer(text=empty_actions_text, reply_markup=markup)


async def del_action(call: CallbackQuery, callback_data: ActionCD) -> None:
    user_id = call.from_user.id
    action_id = callback_data.action_id
    markup = await menu_inline_kb(actions_menu_buttons)
    returning = await delete_action(user_id, action_id)
    if returning:
        await call.message.edit_text(text=f"{rm_action_text} {callback_data.action_name}", reply_markup=markup)
    else:
        await call.message.edit_text(text=f"{action_not_exists_text} {callback_data.action_name}", reply_markup=markup)
