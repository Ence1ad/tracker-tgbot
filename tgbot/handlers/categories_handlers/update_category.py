from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.categories.categories_commands import update_category, get_categories_without_actions
from tgbot.keyboards.buttons_names import category_menu_buttons
from tgbot.keyboards.menu_kb import menu_inline_kb
from tgbot.keyboards.categories_kb import list_categories_inline_kb
from tgbot.utils.answer_text import upd_category_text, new_category_text, select_category_text, empty_categories_text
from tgbot.utils.callback_data_classes import UpdateCategoryCallback
from tgbot.utils.states import UpdateCategoryState


async def select_category(call: CallbackQuery, state: FSMContext, callback_data: UpdateCategoryCallback):
    await call.message.delete()
    await call.message.answer(text=new_category_text)
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(UpdateCategoryState.GET_NAME)


async def select_update_category(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await call.message.delete()
    categories: list = list(await get_categories_without_actions(user_id))
    if categories:
        markup = await list_categories_inline_kb(categories, UpdateCategoryCallback)
        await call.message.answer(text=select_category_text, reply_markup=markup)
        await state.set_state(UpdateCategoryState.GET_NAME)
    else:
        markup = await menu_inline_kb(dict(create_categories='🆕 Create category'))
        await call.message.answer(text=empty_categories_text, reply_markup=markup)


async def upd_category(message: Message, state: FSMContext):
    await state.update_data(category_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    await state.clear()
    new_category_name = state_data['category_name'].strip()[:29]
    await update_category(user_id, state_data['category_id'], new_category_name)
    markup = await menu_inline_kb(category_menu_buttons)
    await message.answer(text=f"{upd_category_text} {new_category_name}", reply_markup=markup)
