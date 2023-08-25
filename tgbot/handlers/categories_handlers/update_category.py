from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.categories.categories_commands import update_category, select_categories
from tgbot.handlers.categories_handlers.show_categories import is_category_available
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.buttons_names import category_menu_buttons, new_category_button
from tgbot.utils.answer_text import upd_category_text, new_category_text, select_category_text, empty_categories_text, \
    categories_is_fake_text
from tgbot.keyboards.callback_factories import CategoryOperation, CategoryCD
from tgbot.utils.states import UpdateCategoryState


async def select_category(call: CallbackQuery, state: FSMContext, callback_data: CategoryCD):
    # await call.message.delete()
    await call.message.edit_text(text=new_category_text)
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(UpdateCategoryState.GET_NAME)


async def select_update_category(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    # await call.message.delete()
    categories: list = list(await select_categories(user_id))
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.UDP)
        await call.message.edit_text(text=select_category_text, reply_markup=markup)
        await state.set_state(UpdateCategoryState.GET_NAME)
    else:
        markup = await menu_inline_kb(new_category_button)
        await call.message.edit_text(text=empty_categories_text, reply_markup=markup)


async def upd_category(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(category_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    await state.clear()
    new_category_name = state_data['category_name']
    category_id = state_data['category_id']
    markup = await menu_inline_kb(category_menu_buttons)
    is_category: bool = await is_category_available(user_id, cb_category_id=category_id)
    if is_category:
        return await message.answer(text=categories_is_fake_text, reply_markup=markup)
    await update_category(user_id, state_data['category_id'], new_category_name)

    await message.answer(text=f"{upd_category_text} {new_category_name}", reply_markup=markup)
