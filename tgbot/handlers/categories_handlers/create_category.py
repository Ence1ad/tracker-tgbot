from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from db.categories.categories_commands import create_category, select_categories
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.states import CategoryState
from tgbot.utils.validators import valid_name


async def prompt_new_category_handler(call: CallbackQuery, state: FSMContext, i18n: TranslatorRunner,
                                      db_session: async_sessionmaker[AsyncSession], buttons: AppButtons) -> Message:
    """
    The prompt_new_category_handler function is called when the user clicks on the &quot;New category&quot; button in
    the categories' menu. It checks if the user has reached his limit of categories and, if not, prompts him to enter
    a name for his new category.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param state: FSMContext: Store the state of the conversation between user and bot
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :return: A message with a request to enter the name of the new category
    """
    user_id: int = call.from_user.id
    categories: list[Row] = await select_categories(user_id, db_session)
    if categories and (len(categories) >= settings.USER_CATEGORIES_LIMIT):
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
        await state.clear()
        return await call.message.edit_text(
            text=i18n.get("category_limit_text", category_limit=settings.USER_CATEGORIES_LIMIT), reply_markup=markup)
    else:
        await state.set_state(CategoryState.GET_NAME)
        return await call.message.edit_text(text=i18n.get('new_category_text'))


async def create_category_handler(message: Message, state: FSMContext, i18n: TranslatorRunner,
                                  db_session: async_sessionmaker[AsyncSession], buttons: AppButtons) -> Message:
    """
    The create_category_handler function is responsible for creating a new category.
    It checks if the user has entered a valid name, and if so, creates it in the database.
    If not, it returns an error message to the user.

    :param message: Message: Get the message object that was sent by the user
    :param state: FSMContext: Store the state of the conversation between user and bot
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text and a menu inline keyboard
    """
    user_id: int = message.from_user.id
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)

    if not isinstance(message.text, str):
        return await message.answer(text=i18n.get('new_valid_action_name', new_line='\n'), reply_markup=markup)
    user_categories: list[Row] = await select_categories(user_id, db_session)
    await state.update_data(category_name=message.text)
    state_data: dict = await state.get_data()
    new_category_name: str = state_data['category_name']
    if new_category_valid_name := await valid_name(user_categories, new_category_name):
        await state.clear()
        await create_category(user_id, new_category_valid_name, db_session)
        return await message.answer(text=i18n.get('added_new_category_text'), reply_markup=markup)
    else:
        return await message.answer(
            text=i18n.get('category_exists_text', new_category_name=new_category_name, new_line='\n'))
