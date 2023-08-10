from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import ScalarResult

from db.categories.categories_commands import create_category, get_categories, delete_category, update_category
from tgbot.keyboards.categories_kb import categories_custom_inline_kb, remove_category_inline_kb, \
    update_category_inline_kb, DeleteCategoryCallback, UpdateCategoryCallback
from tgbot.utils.answer_text import categories_options_text, new_category_text, added_new_category_text, \
    show_categories_text, empty_categories_text, select_category_text, rm_category_text, upd_category_text
from tgbot.utils.states import CategoryState, UpdateCategoryState


async def get_categories_options(call: CallbackQuery):
    await call.message.delete()
    markup = await categories_custom_inline_kb()
    await call.message.answer(text=categories_options_text, reply_markup=markup)


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
    await message.answer(text=added_new_category_text)
    # else:
    #     await call.message.answer(text=f'You can use only characters and numbers')


async def display_categories(call: CallbackQuery):
    categories: list = list(await show_user_category(call))
    if categories:
        cats_in_column = ''
        for category in categories:
            cats_in_column += category.category_name + '\n\r'
        await call.message.answer(text=f"{show_categories_text}\n\r{cats_in_column}")
    else:
        await call.message.answer(text=empty_categories_text)


#
async def select_remove_category(call: CallbackQuery):
    categories: list = list(await show_user_category(call))
    if categories:
        markup = await remove_category_inline_kb(categories)
        await call.message.answer(text=select_category_text, reply_markup=markup)
    else:
        await call.message.answer(text=empty_categories_text)


async def del_category(call: CallbackQuery, callback_data: DeleteCategoryCallback):
    user_id = call.from_user.id
    await call.message.delete()
    category_id = callback_data.category_id
    await delete_category(user_id, category_id)
    await call.message.answer(text=f"{rm_category_text} {callback_data.category_name}")


async def show_user_category(call: CallbackQuery) -> ScalarResult:
    user_id = call.from_user.id
    await call.message.delete()
    categories: ScalarResult = await get_categories(user_id)
    return categories


async def select_update_category(call: CallbackQuery, state: FSMContext):
    categories: list = list(await show_user_category(call))
    if categories:
        markup = await update_category_inline_kb(categories)
        await call.message.answer(text=select_category_text, reply_markup=markup)
        await state.set_state(UpdateCategoryState.GET_NAME)
    else:
        await call.message.answer(text=empty_categories_text)


async def upd_category(message: Message, state: FSMContext):
    await state.update_data(category_name=message.text)
    user_id = message.from_user.id
    # await message.message.delete()

    state_data = await state.get_data()
    await state.clear()
    new_category_name = state_data['category_name'].strip()[:29]
    await update_category(user_id, state_data['category_id'], new_category_name)
    await message.answer(text=f"{upd_category_text} {new_category_name}")


async def select_category(call: CallbackQuery, state: FSMContext, callback_data: UpdateCategoryCallback):
    await call.message.delete()
    await call.message.answer(text=new_category_text)
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(UpdateCategoryState.GET_NAME)
