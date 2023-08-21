from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from cache.redis_cache import redis_client
from settings import USER_ACTIONS_COUNT, LENGTH_ACTION_NAME_LIMIT
from tgbot.keyboards.buttons_names import actions_menu_buttons, action_limit_btn
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.answer_text import new_action_text, added_new_action_text, action_limit_text, \
    action_exists_text, char_limit, accept_only_text
from tgbot.utils.states import ActionState

from db.actions.actions_db_commands import create_actions, select_actions


async def new_action(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(text=new_action_text + char_limit)
    await state.set_state(ActionState.GET_NAME)


async def get_action_name_from_user(message: Message, state: FSMContext) -> None:
    user_id: int = message.from_user.id
    await state.update_data(action_name=message.text)
    state_data = await state.get_data()
    # If message not a text message
    if not state_data['action_name']:
        await message.answer(text=f"{accept_only_text}")

    else:  # If message a text
        category_id = int(await redis_client.hget(name=user_id, key="category_id"))

        user_actions = await select_actions(user_id, category_id=category_id)

        checking = await _check_action(user_actions, state_data['action_name'])
        if checking and (checking in state_data['action_name']):
            await state.clear()
            await create_actions(user_id, checking, category_id=category_id)
            markup = await menu_inline_kb(actions_menu_buttons)
            await message.answer(text=f"{added_new_action_text}: {checking}", reply_markup=markup)
        elif checking == "action_limit":
            await state.clear()
            markup = await menu_inline_kb(action_limit_btn)
            await message.answer(text=action_limit_text, reply_markup=markup)
        else:
            await message.answer(
                text=f"{state_data['action_name']} {action_exists_text}")


async def _check_action(actions, action_name):
    user_actions = actions.all()
    action_limit = USER_ACTIONS_COUNT
    if len(user_actions) < action_limit:
        for action in user_actions:
            if str(action_name) in action:
                return None
        else:
            return action_name[:LENGTH_ACTION_NAME_LIMIT]
    else:
        return 'action_limit'
