from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.operations.categories_operations import create_category, select_categories
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import CategoryState
from tgbot.utils.validators import valid_name


async def prompt_new_category_handler(
        call: CallbackQuery, state: FSMContext, i18n: TranslatorRunner,
        db_session: AsyncSession, buttons: AppButtons
) -> Message:
    """Handle the callback for prompting the user to enter a new category name.

    :param call: CallbackQuery: The callback query triggered by the user.
    :param state: FSMContext: The FSM (Finite State Machine) context for tracking the
     user's state.
    :param i18n: TranslatorRunner: An instance of the translation runner for
    internationalization.
    :param db_session: AsyncSession: An asynchronous database session.
    :param buttons: AppButtons: An instance of the application buttons.
    :return:  Message: A message to prompt the user for a new category name.
    """
    user_id: int = call.from_user.id
    categories: Sequence = await select_categories(user_id, db_session)
    if categories and (len(categories) >= settings.USER_CATEGORIES_LIMIT):
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.categories_btn_source.category_menu_buttons(),
            i18n)
        await state.clear()
        return await call.message.edit_text(
            text=i18n.get("category_limit_text",
                          category_limit=settings.USER_CATEGORIES_LIMIT),
            reply_markup=markup)
    else:
        await state.set_state(CategoryState.GET_NAME)
        return await call.message.edit_text(text=i18n.get('new_category_text'))


async def create_category_handler(
        message: Message, state: FSMContext, i18n: TranslatorRunner,
        db_session: AsyncSession, buttons: AppButtons
) -> Message:
    """Handle the user's input for creating a new category.

    :param message: Message: The user's message containing the new category name.
    :param state: FSMContext: The FSM (Finite State Machine) context for tracking the
        user's state.
    :param i18n: TranslatorRunner: An instance of the translation runner for
    internationalization.
    :param db_session: AsyncSession: An asynchronous database session.
    :param buttons: AppButtons: An instance of the application buttons.
    :return: Message: A response message to inform the user about the status of the new
     category creation.
    """
    user_id: int = message.from_user.id
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.categories_btn_source.category_menu_buttons(),
        i18n)
    user_categories: Sequence = await select_categories(user_id, db_session)
    await state.update_data(category_name=message.text)
    state_data: dict = await state.get_data()
    new_category_name: str = state_data['category_name']
    if new_category_valid_name := await valid_name(user_categories, new_category_name):
        await state.clear()
        await create_category(user_id, new_category_valid_name, db_session)
        return await message.answer(text=i18n.get('added_new_category_text'),
                                    reply_markup=markup)
    else:
        return await message.answer(
            text=i18n.get('category_exists_text', new_category_name=new_category_name,
                          new_line='\n'))
