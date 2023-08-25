from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from cache.redis_commands import redis_hget_category_id
from db.actions.actions_db_commands import update_action, select_category_actions, action_exists
from tgbot.handlers.categories_handlers.show_categories import is_category_available
from tgbot.utils.validators import valid_name
from tgbot.keyboards.buttons_names import actions_menu_buttons, new_action_button, select_action_button
from tgbot.handlers.actions_handlers.show_actions import show_user_actions
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import ActionOperation, ActionCD
from tgbot.utils.states import UpdateActionState
from tgbot.utils.answer_text import new_action_text, empty_actions_text, upd_action_text, \
    accept_only_text, action_exists_text, action_not_exists_text, to_update_action_text,  \
    categories_is_fake_text


async def select_action(call: CallbackQuery, state: FSMContext, callback_data: ActionCD):
    await call.message.edit_text(text=new_action_text)
    await state.clear()
    await state.update_data(action_id=callback_data.action_id)
    await state.set_state(UpdateActionState.GET_NAME)


async def update_action_reaction_handler(call: CallbackQuery, state: FSMContext):
    action: list = list(await show_user_actions(call))
    if action:
        markup = await callback_factories_kb(action, ActionOperation.UDP)
        await call.message.edit_text(text=to_update_action_text, reply_markup=markup)
        await state.set_state(UpdateActionState.GET_NAME)
    else:
        markup = await menu_inline_kb(new_action_button)
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)


async def upd_action(message: Message, state: FSMContext):
    await state.update_data(action_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    new_action_name: str = state_data['action_name']
    action_id = state_data['action_id']

    # Is the text checking
    if not new_action_name:
        await message.answer(text=f"{accept_only_text}")

    is_category: bool = await is_category_available(user_id)
    if not is_category:
        markup = await menu_inline_kb(select_action_button)
        return await message.answer(text=categories_is_fake_text, reply_markup=markup)

    else:  # If message a text
        is_action = await action_exists(user_id, action_id)
        # Check if the category is available
        if not is_action:
            markup = await menu_inline_kb(actions_menu_buttons)
            return await message.answer(text=f"{action_not_exists_text}", reply_markup=markup)
        # Get category_id from cache
        category_id: int = await redis_hget_category_id(user_id)
        user_actions = await select_category_actions(user_id, category_id=category_id)
        checking_availability = await valid_name(user_actions, new_action_name)
        if checking_availability:
            await update_action(user_id, action_id, new_action_name)
            markup = await menu_inline_kb(actions_menu_buttons)
            await state.clear()
            return await message.answer(text=f"{upd_action_text} {new_action_name}", reply_markup=markup)
        else:
            return await message.answer(text=f"{new_action_name} {action_exists_text}")
