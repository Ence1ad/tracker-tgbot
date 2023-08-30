from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.actions.actions_db_commands import update_action, select_category_actions
from tgbot.utils.validators import valid_name
from tgbot.keyboards.buttons_names import actions_menu_buttons, new_action_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import ActionOperation, ActionCD
from tgbot.utils.states import UpdateActionState, ActionState
from tgbot.utils.answer_text import new_action_text, empty_actions_text, upd_action_text, \
    accept_only_text, action_exists_text, action_not_exists_text, to_update_action_text


async def select_action(call: CallbackQuery, state: FSMContext, callback_data: ActionCD):
    await call.message.edit_text(text=new_action_text)
    await state.update_data(action_id=callback_data.action_id)
    await state.set_state(UpdateActionState.GET_NAME)


async def update_action_reaction_handler(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    user_id = call.from_user.id
    state_data = await state.get_data()
    # Get category_id from cache
    category_id = state_data['category_id']
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.UDP)
        await call.message.edit_text(text=to_update_action_text, reply_markup=markup)
        await state.set_state(UpdateActionState.GET_NAME)
    else:
        markup = await menu_inline_kb(new_action_button)
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)


async def upd_action(message: Message, state: FSMContext, db_session: AsyncSession):
    await state.update_data(action_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    new_action_name: str = state_data['action_name']
    action_id = state_data['action_id']
    category_name = state_data['category_name']

    # Is the text checking
    if not new_action_name:
        await message.answer(text=f"{accept_only_text}")

    else:  # If message a text
        state_data = await state.get_data()
        # Get category_id from cache
        category_id = state_data['category_id']
        user_actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        checking_availability = await valid_name(user_actions, new_action_name)
        if checking_availability:
            returning = await update_action(user_id, action_id, checking_availability, db_session=db_session)
            await state.set_state(ActionState.WAIT_CATEGORY_DATA)
            markup = await menu_inline_kb(actions_menu_buttons)
            if returning:
                return await message.answer(text=
                                            f"{upd_action_text} - {new_action_name} for category - {category_name}",
                                            reply_markup=markup)
            else:
                return await message.answer(text=f"{action_not_exists_text}", reply_markup=markup)
        else:
            return await message.answer(text=f"{new_action_name} {action_exists_text}")
