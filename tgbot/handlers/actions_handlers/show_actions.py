from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.actions.actions_db_commands import select_category_actions
from tgbot.keyboards.callback_factories import CategoryCD
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons

from tgbot.utils.answer_text import empty_actions_text, categories_options_text, show_action_text
from tgbot.utils.states import ActionState


async def get_actions_options(call: CallbackQuery, callback_data: CategoryCD, state: FSMContext, buttons: AppButtons
                              ) -> None:
    await state.update_data(category_id=callback_data.category_id, category_name=callback_data.category_name)
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)

    markup = await menu_inline_kb(await buttons.action_menu_buttons())
    await call.message.edit_text(
        text=f"Selected category -> <i>{callback_data.category_name}</i>\n\r{categories_options_text}",
        reply_markup=markup
    )


async def display_actions(call: CallbackQuery, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                          buttons: AppButtons) -> None:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    category_name = state_data['category_name']
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        await call.message.delete()
        markup = await menu_inline_kb(await buttons.action_menu_buttons())
        act_in_column = ''.join([action.action_name + '\n\r' for action in actions])
        await call.message.answer(
            text=f"{show_action_text}<i>{category_name}</i>:\n\r{act_in_column}",
            reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.new_action())
        await call.message.edit_text(text=empty_actions_text, reply_markup=markup)
