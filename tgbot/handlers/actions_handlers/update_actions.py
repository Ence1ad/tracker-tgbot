from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.actions.actions_db_commands import update_action
from tgbot.handlers.actions_handlers.show_actions import show_user_actions
from tgbot.keyboards.actions_kb import list_actions_inline_kb
from tgbot.utils.answer_text import new_action_text, select_action_text, empty_actions_text, upd_action_text
from tgbot.utils.states import UpdateActionState


class UpdateActionCallback(CallbackData, prefix="udp_act"):
    action_id: int
    action_name: str


async def select_action(call: CallbackQuery, state: FSMContext, callback_data: UpdateActionCallback):
    await call.message.delete()
    await call.message.answer(text=new_action_text)
    await state.clear()
    await state.update_data(action_id=callback_data.action_id)
    await state.set_state(UpdateActionState.GET_NAME)


async def select_update_action(call: CallbackQuery, state: FSMContext):
    action: list = list(await show_user_actions(call))
    if action:
        markup = await list_actions_inline_kb(action, UpdateActionCallback)
        await call.message.answer(text=select_action_text, reply_markup=markup)
        await state.set_state(UpdateActionState.GET_NAME)
    else:
        await call.message.answer(text=empty_actions_text)


async def upd_action(message: Message, state: FSMContext):
    await state.update_data(action_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    await state.clear()
    new_action_name = state_data['action_name'].strip()[:29]
    await update_action(user_id, state_data['action_id'], new_action_name)
    await message.answer(text=f"{upd_action_text} {new_action_name}")