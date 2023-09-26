from enum import Enum

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.actions.actions_db_commands import select_category_actions
from tgbot.keyboards.callback_factories import CategoryCD, ActionOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.keyboards.app_buttons import AppButtons

from tgbot.utils.states import ActionState


async def get_actions_options(call: CallbackQuery, callback_data: CategoryCD, state: FSMContext, buttons: AppButtons,
                              i18n: TranslatorRunner, db_session: async_sessionmaker[AsyncSession]) -> Message:
    user_id = call.from_user.id
    category_id = callback_data.category_id
    category_name = callback_data.category_name
    await state.update_data(category_id=category_id, category_name=category_name)
    await state.set_state(ActionState.WAIT_CATEGORY_DATA)
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    markup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
    if actions:
        actions_list_text = await _actions_list(actions)
        return await call.message.edit_text(text=i18n.get('selected_category', category_name=category_name,
                                                          new_line='\n', actions_list_text=actions_list_text),
                                            reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)


async def display_actions(call: CallbackQuery, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                          buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    category_name = state_data['category_name']
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
        await call.message.delete()
        actions_list_text = await _actions_list(actions)
        return await call.message.answer(text=i18n.get('show_action_text', category_name=category_name,
                                         new_line='\n', actions_list_text=actions_list_text), reply_markup=markup)
    else:

        markup = await menu_inline_kb(await buttons.new_action(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)


async def _actions_list(model: list[Row]) -> str:
    act_column = ''.join([f"{idx}. {action.action_name}\n\r" for idx, action in enumerate(model, 1)])
    return act_column


async def get_actions_handler(call: CallbackQuery, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                              buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    operation = await _get_action_operation(call_data=call.data, buttons=buttons)
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        markup = await callback_factories_kb(actions, operation)
        return await call.message.edit_text(text=i18n.get('select_action_text'), reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_actions_text'), reply_markup=markup)


async def _get_action_operation(call_data: str, buttons: AppButtons) -> Enum:
    operation = None
    if call_data == buttons.actions_data.UPDATE_ACTIONS.name:
        operation = ActionOperation.UPD
    elif call_data == buttons.actions_data.DELETE_ACTIONS.name:
        operation = ActionOperation.DEL
    return operation
