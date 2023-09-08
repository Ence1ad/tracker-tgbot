from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.actions.actions_db_commands import select_category_actions
from tgbot.keyboards.buttons_names import new_action_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import empty_actions_text, select_action_text
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation
from tgbot.utils.states import TrackerState, ActionState


async def display_actions_tracker(call: CallbackQuery, callback_data: CategoryCD, state: FSMContext,
                                  db_session: async_sessionmaker[AsyncSession]) -> None:
    user_id = call.from_user.id
    actions = await select_category_actions(user_id, category_id=callback_data.category_id, db_session=db_session)
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.READ_TRACKER)
        await call.message.edit_text(
            text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{select_action_text}",
            reply_markup=markup)
        await state.update_data(category_id=callback_data.category_id, category_name=callback_data.category_name)
        await state.set_state(TrackerState.WAIT_CATEGORY_DATA)
    else:
        await state.update_data(category_id=callback_data.category_id, category_name=callback_data.category_name)
        await state.set_state(ActionState.WAIT_CATEGORY_DATA)
        markup = await menu_inline_kb(new_action_button)
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)
