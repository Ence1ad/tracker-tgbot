from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from settings import USER_ACTIONS_LIMIT
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import category_menu_buttons, category_limit_btn
from tgbot.utils.answer_text import new_category_text, added_new_category_text, category_exists_text, \
    category_limit_text
from tgbot.utils.states import CategoryState

from db.categories.categories_commands import create_category, select_categories
from tgbot.utils.validators import valid_name


async def new_category(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await call.message.edit_text(text=new_category_text)
    categories = await select_categories(user_id)
    if categories and (len(categories) >= USER_ACTIONS_LIMIT):
        markup = await menu_inline_kb(category_limit_btn)
        await state.clear()
        return await call.message.edit_text(text=category_limit_text, reply_markup=markup)
    else:
        await state.set_state(CategoryState.GET_NAME)


async def get_category_name_from_user(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    await state.update_data(category_name=message.text)
    state_data = await state.get_data()
    category_name = state_data['category_name']
    user_categories = await select_categories(user_id)
    checking_name = await valid_name(user_categories, category_name)

    if checking_name:
        await state.clear()
        await create_category(user_id, checking_name)
        markup = await menu_inline_kb(category_menu_buttons)
        await message.answer(text=added_new_category_text, reply_markup=markup)

    else:
        await message.answer(
            text=f"{category_name} {category_exists_text}")
