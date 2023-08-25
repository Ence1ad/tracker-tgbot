from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from cache.redis_commands import redis_hget_category_id
from settings import USER_ACTIONS_LIMIT
from tgbot.handlers.categories_handlers.show_categories import is_category_available
from tgbot.keyboards.buttons_names import actions_menu_buttons, action_limit_btn, select_action_button
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import new_action_text, added_new_action_text, action_limit_text, \
    action_exists_text, char_limit, accept_only_text, categories_is_fake_text
from tgbot.utils.states import ActionState

from db.actions.actions_db_commands import create_actions, select_category_actions, select_action_count
from tgbot.utils.validators import valid_name


async def new_action_reaction_handler(call: CallbackQuery, state: FSMContext) -> Message | None:
    user_id = call.from_user.id
    # Get category_id from cache
    is_category: bool = await is_category_available(user_id)
    if is_category:
        markup = await menu_inline_kb(select_action_button)
        return await call.message.edit_text(text=categories_is_fake_text, reply_markup=markup)
    # Get category_id from cache
    category_id: int = await redis_hget_category_id(user_id)
    # Get user_actions from db
    action_count: int = await select_action_count(user_id, category_id)
    if action_count >= USER_ACTIONS_LIMIT:
        markup = await menu_inline_kb(action_limit_btn)
        await state.clear()
        return await call.message.edit_text(text=action_limit_text, reply_markup=markup)
    else:
        await state.set_state(ActionState.GET_NAME)
        return await call.message.edit_text(text=new_action_text + char_limit)


async def create_action_handler(message: Message, state: FSMContext) -> None:
    user_id: int = message.from_user.id
    await state.update_data(action_name=message.text)
    state_data = await state.get_data()
    # If message not a text message
    if not state_data['action_name']:
        await message.answer(text=f"{accept_only_text}")
    else:  # If message a text
        # Get category_id from cache
        category_id: int = await redis_hget_category_id(user_id)
        # Get user_actions from db
        user_actions = await select_category_actions(user_id, category_id=category_id)
        checking_name = await valid_name(user_actions, state_data['action_name'])
        if checking_name:
            await create_actions(user_id, checking_name, category_id=category_id)
            markup = await menu_inline_kb(actions_menu_buttons)
            await message.answer(text=f"{added_new_action_text}: {checking_name}", reply_markup=markup)
            await state.clear()
        else:
            await message.answer(
                text=f"{state_data['action_name']} {action_exists_text}")



