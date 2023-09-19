from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import new_category_text, added_new_category_text, category_exists_text, \
    category_limit_text
from tgbot.utils.states import CategoryState

from db.categories.categories_commands import create_category, select_categories
from tgbot.utils.validators import valid_name


async def prompt_new_category_handler(call: CallbackQuery, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                                      buttons: AppButtons) -> Message | FSMContext:
    user_id = call.from_user.id
    await call.message.edit_text(text=new_category_text)
    categories = await select_categories(user_id, db_session)
    if categories and (len(categories) >= settings.USER_CATEGORIES_LIMIT):
        markup = await menu_inline_kb(await buttons.category_limit_menu())
        await state.clear()
        return await call.message.edit_text(text=category_limit_text, reply_markup=markup)
    else:
        await state.set_state(CategoryState.GET_NAME)
        return state


async def create_category_handler(message: Message, state: FSMContext,
                                  db_session: async_sessionmaker[AsyncSession], buttons: AppButtons) -> Message:
    user_id: int = message.from_user.id
    await state.update_data(category_name=message.text)
    state_data = await state.get_data()
    new_category_name = state_data['category_name']
    user_categories = await select_categories(user_id, db_session)
    new_category_valid_name = await valid_name(user_categories, new_category_name)

    if new_category_valid_name:
        await state.clear()
        await create_category(user_id, new_category_valid_name, db_session)
        markup = await menu_inline_kb(await buttons.category_menu_buttons())
        return await message.answer(text=added_new_category_text, reply_markup=markup)

    else:
        return await message.answer(
            text=f"{new_category_name} {category_exists_text}")