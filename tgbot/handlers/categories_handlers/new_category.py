from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.menu_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import actions_menu_buttons
from tgbot.utils.answer_text import new_category_text, added_new_category_text
from tgbot.utils.states import CategoryState

from db.categories.categories_commands import create_category


async def new_category(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text=new_category_text)
    await state.set_state(CategoryState.GET_NAME)


async def get_category_name_from_user(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    await state.update_data(category_name=message.text)
    state_data = await state.get_data()
    await state.clear()
    await create_category(user_id, state_data['category_name'].strip()[:29])
    markup = await menu_inline_kb(actions_menu_buttons)
    await message.answer(text=added_new_category_text, reply_markup=markup)
