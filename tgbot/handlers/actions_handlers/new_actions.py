from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.handlers.actions_handlers.show_actions import USER_CATEGORY
from tgbot.utils.answer_text import new_action_text, added_new_action_text
from tgbot.utils.states import ActionState

from db.actions.actions_db_commands import create_actions

# Todo сделать ограничение на 15 активностей
async def new_action(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text=new_action_text)
    await state.set_state(ActionState.GET_NAME)


async def get_action_name_from_user(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    await state.update_data(category_name=message.text)
    state_data = await state.get_data()
    await state.clear()
    await create_actions(user_id, state_data['category_name'].strip()[:29], category_id=USER_CATEGORY[user_id])
    await message.answer(text=added_new_action_text)
