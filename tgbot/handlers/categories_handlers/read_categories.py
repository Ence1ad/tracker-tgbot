from enum import Enum

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.categories.categories_commands import select_categories

from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb


async def display_categories(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                             buttons: AppButtons, i18n: TranslatorRunner, state: FSMContext) -> Message:
    user_id = call.from_user.id
    await call.message.delete()
    await state.clear()
    categories = await select_categories(user_id, db_session)
    if categories:
        columns_list_text = await _categories_list(categories)
        markup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
        return await call.message.answer(text=f"{i18n.get('show_categories_text')}\n\r{columns_list_text}",
                                         reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.new_category(), i18n)
        return await call.message.answer(text=i18n.get('empty_categories_text'), reply_markup=markup)


async def _categories_list(model: list[Row]) -> str:
    cat_column = ''.join([f"{idx}. {category.category_name}\n\r" for idx, category in enumerate(model, 1)])
    return cat_column


async def get_categories(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession], buttons: AppButtons,
                         i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    operation = await _get_operation(call_data=call.data, buttons=buttons)
    categories = await select_categories(user_id, db_session)
    if categories:
        markup = await callback_factories_kb(categories, operation)
        return await call.message.edit_text(text=i18n.get('select_category_text'), reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.new_category(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_categories_text'), reply_markup=markup)


async def _get_operation(call_data: str, buttons: AppButtons) -> Enum:
    operation = None
    if call_data == buttons.general_data.ACTIONS_BTN.name:
        operation = CategoryOperation.READ
    elif call_data == buttons.categories_data.UPDATE_CATEGORIES.name:
        operation = CategoryOperation.UPD
    elif call_data == buttons.categories_data.DELETE_CATEGORIES.name:
        operation = CategoryOperation.DEL
    return operation
