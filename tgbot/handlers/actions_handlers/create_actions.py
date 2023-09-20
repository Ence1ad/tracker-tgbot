from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import ActionState

from db.actions.actions_db_commands import create_actions, select_category_actions
from tgbot.utils.validators import valid_name


async def prompt_new_action_handler(call: CallbackQuery, state: FSMContext,  i18n: TranslatorRunner,
                                    db_session: async_sessionmaker[AsyncSession], buttons: AppButtons
                                    ) -> Message | None:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    # Get user_actions from db
    action_count: int = len(await select_category_actions(user_id, category_id, db_session))
    if action_count >= settings.USER_ACTIONS_LIMIT:
        markup = await menu_inline_kb(await buttons.action_limit_menu(), i18n)
        return await call.message.edit_text(text=i18n.get('action_limit_text'), reply_markup=markup)
    else:
        await state.set_state(ActionState.GET_NAME)
        return await call.message.edit_text(text=i18n.get('new_action_text'))


async def create_action_handler(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                                buttons: AppButtons,  i18n: TranslatorRunner) -> None:
    user_id: int = message.from_user.id
    await state.update_data(action_name=message.text)
    state_data = await state.get_data()
    # Get category_id from cache
    category_id = state_data['category_id']
    new_action_name = state_data['action_name']
    # If message not a text message
    if not new_action_name:
        await message.answer(text=f"{i18n.get('accept_only_text')}")
    else:  # If message a text
        # Get user_actions from db
        user_actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
        new_action_valid_name = await valid_name(user_actions, new_action_name)
        if new_action_valid_name:
            await create_actions(user_id, new_action_valid_name, category_id=category_id, db_session=db_session)
            markup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
            await message.answer(text=f"{i18n.get('added_new_action_text')}: {new_action_valid_name}",
                                 reply_markup=markup)
            await state.set_state(ActionState.WAIT_CATEGORY_DATA)
        else:
            await message.answer(
                text=f"{new_action_name} {i18n.get('action_exists_text')}")
