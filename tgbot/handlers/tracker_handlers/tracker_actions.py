from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.actions.actions_db_commands import select_category_actions
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation
from tgbot.utils.states import TrackerState, ActionState


async def display_actions_tracker(call: CallbackQuery, callback_data: CategoryCD, state: FSMContext,
                                  db_session: async_sessionmaker[AsyncSession], buttons: AppButtons,
                                  i18n: TranslatorRunner) -> None:
    user_id = call.from_user.id
    category_id = callback_data.category_id
    category_name = callback_data.category_name
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup = await callback_factories_kb(actions, ActionOperation.READ_TRACKER)
        await call.message.edit_text(
            text=i18n.get('select_category_4_tracker', category_name=category_name), reply_markup=markup)
        await state.update_data(category_id=callback_data.category_id, category_name=category_name)
        await state.set_state(TrackerState.WAIT_CATEGORY_DATA)
    else:
        await state.update_data(category_id=callback_data.category_id, category_name=category_name)
        await state.set_state(ActionState.WAIT_CATEGORY_DATA)
        markup = await menu_inline_kb(await buttons.new_action(), i18n)
        await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)
